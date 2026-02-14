"""
Proposition de visualisations via Ollama Mistral
"""

import requests
import json
from typing import Dict, Any, List


class VizProposer:
    """Générateur de propositions avec Mistral local"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "mistral-opt"
    
    def propose_visualizations(self, question: str, df_info: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génère 3 propositions de visualisations"""
        
        prompt = f"""Propose 3 visualisations DIFFÉRENTES.

PROBLÉMATIQUE: "{question}"
COLONNES NUMÉRIQUES: {', '.join(df_info.get('numeric_columns', []))}
COLONNES CATÉGORIELLES: {', '.join(df_info.get('categorical_columns', []))}

Types disponibles: bar_chart, scatter_plot, histogram, box_plot

IMPORTANT: Pour chaque visualisation, x_axis et y_axis doivent être des noms de colonnes valides (pas null, pas "None").

Réponds en JSON uniquement:
{{
  "proposals": [
    {{"id": 1, "type": "scatter_plot", "title": "Titre 1", "x_axis": "colonne1", "y_axis": "colonne2", "color": null, "rationale": "Pourquoi"}},
    {{"id": 2, "type": "bar_chart", "title": "Titre 2", "x_axis": "colonne3", "y_axis": "colonne4", "color": null, "rationale": "Raison"}},
    {{"id": 3, "type": "histogram", "title": "Titre 3", "x_axis": "colonne5", "y_axis": "count", "color": null, "rationale": "Raison"}}
  ]
}}"""
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=30
            )
            content = response.json()["response"]
            
            # Extraire le JSON
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                content = content[start:end]
            
            result = json.loads(content)
            proposals = result.get("proposals", [])
            
            # VALIDATION: Vérifier que chaque proposition est valide
            validated_proposals = []
            for prop in proposals:
                if self._validate_proposal(prop, df_info):
                    validated_proposals.append(prop)
            
            # Si pas assez de propositions valides, ajouter des fallbacks
            while len(validated_proposals) < 3:
                fallback = self._get_single_fallback(
                    len(validated_proposals) + 1, 
                    df_info
                )
                if fallback:
                    validated_proposals.append(fallback)
                else:
                    break
            
            return validated_proposals[:3]
            
        except:
            return self._get_default_proposals(df_info)
    
    def _validate_proposal(self, proposal: Dict[str, Any], df_info: Dict[str, Any]) -> bool:
        """Valide qu'une proposition est correcte"""
        
        # Vérifier les champs requis
        if not all(k in proposal for k in ['id', 'type', 'title', 'x_axis', 'y_axis']):
            return False
        
        x_axis = proposal.get('x_axis')
        y_axis = proposal.get('y_axis')
        
        # x_axis ne doit jamais être None
        if x_axis is None or x_axis == 'None' or x_axis == '':
            return False
        
        # y_axis peut être 'count' pour histogram, sinon doit être une colonne
        if y_axis is None or y_axis == 'None' or y_axis == '':
            # Accepter seulement si c'est un histogram
            if proposal.get('type') != 'histogram':
                return False
            else:
                # Forcer y_axis à 'count' pour histogram
                proposal['y_axis'] = 'count'
        
        # Vérifier que les colonnes existent (sauf 'count')
        all_cols = df_info.get('columns', [])
        
        if x_axis != 'count' and x_axis not in all_cols:
            return False
        
        if y_axis != 'count' and y_axis not in all_cols:
            return False
        
        return True
    
    def _get_single_fallback(self, proposal_id: int, df_info: Dict[str, Any]) -> Dict[str, Any]:
        """Génère une seule proposition fallback"""
        numeric = df_info.get('numeric_columns', [])
        categoric = df_info.get('categorical_columns', [])
        
        if proposal_id == 1 and len(numeric) >= 2:
            return {
                "id": 1, 
                "type": "scatter_plot",
                "title": f"Relation entre {numeric[0]} et {numeric[1]}",
                "x_axis": numeric[0], 
                "y_axis": numeric[1],
                "color": None,
                "rationale": "Nuage de points pour explorer la corrélation"
            }
        
        elif proposal_id == 2 and categoric and numeric:
            return {
                "id": 2, 
                "type": "bar_chart",
                "title": f"Moyenne de {numeric[0]} par {categoric[0]}",
                "x_axis": categoric[0], 
                "y_axis": numeric[0],
                "color": None,
                "rationale": "Comparaison des moyennes par catégorie"
            }
        
        elif proposal_id == 3 and numeric:
            return {
                "id": 3, 
                "type": "histogram",
                "title": f"Distribution de {numeric[0]}",
                "x_axis": numeric[0], 
                "y_axis": "count",
                "color": None,
                "rationale": "Histogramme pour voir la distribution"
            }
        
        return None
    
    def _get_default_proposals(self, df_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Propositions par défaut complètes"""
        proposals = []
        
        for i in range(1, 4):
            fallback = self._get_single_fallback(i, df_info)
            if fallback:
                proposals.append(fallback)
        
        # Compléter si nécessaire
        numeric = df_info.get('numeric_columns', [])
        categoric = df_info.get('categorical_columns', [])
        
        while len(proposals) < 3:
            if numeric:
                proposals.append({
                    "id": len(proposals) + 1,
                    "type": "histogram",
                    "title": f"Distribution de {numeric[0]}",
                    "x_axis": numeric[0],
                    "y_axis": "count",
                    "color": None,
                    "rationale": "Visualisation de distribution"
                })
            elif categoric and numeric:
                proposals.append({
                    "id": len(proposals) + 1,
                    "type": "bar_chart",
                    "title": f"{numeric[0]} par {categoric[0]}",
                    "x_axis": categoric[0],
                    "y_axis": numeric[0],
                    "color": None,
                    "rationale": "Comparaison par catégorie"
                })
            else:
                break
        
        return proposals[:3]