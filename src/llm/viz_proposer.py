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
        self.model = "mistral"
    
    def propose_visualizations(self, question: str, df_info: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génère 3 propositions de visualisations"""
        
        prompt = f"""Propose 3 visualisations DIFFÉRENTES.

PROBLÉMATIQUE: "{question}"
COLONNES NUMÉRIQUES: {', '.join(df_info.get('numeric_columns', []))}
COLONNES CATÉGORIELLES: {', '.join(df_info.get('categorical_columns', []))}

Types disponibles: bar_chart, line_chart, scatter_plot, histogram, box_plot

Réponds en JSON uniquement:
{{
  "proposals": [
    {{"id": 1, "type": "scatter_plot", "title": "Titre 1", "x_axis": "colonne1", "y_axis": "colonne2", "color": null, "rationale": "Pourquoi ce graphique"}},
    {{"id": 2, "type": "bar_chart", "title": "Titre 2", "x_axis": "colonne3", "y_axis": "colonne4", "color": null, "rationale": "Autre raison"}},
    {{"id": 3, "type": "histogram", "title": "Titre 3", "x_axis": "colonne5", "y_axis": "count", "color": null, "rationale": "Troisième raison"}}
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
            return result.get("proposals", [])
        except:
            # Fallback simple
            return self._get_default_proposals(df_info)
    
    def _get_default_proposals(self, df_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Propositions par défaut"""
        numeric = df_info.get('numeric_columns', [])
        categoric = df_info.get('categorical_columns', [])
        
        proposals = []
        
        if len(numeric) >= 2:
            proposals.append({
                "id": 1, "type": "scatter_plot",
                "title": f"{numeric[0]} vs {numeric[1]}",
                "x_axis": numeric[0], "y_axis": numeric[1], "color": None,
                "rationale": "Voir la corrélation"
            })
        
        if categoric and numeric:
            proposals.append({
                "id": 2, "type": "bar_chart",
                "title": f"{numeric[0]} par {categoric[0]}",
                "x_axis": categoric[0], "y_axis": numeric[0], "color": None,
                "rationale": "Comparer les catégories"
            })
        
        if numeric:
            proposals.append({
                "id": 3, "type": "histogram",
                "title": f"Distribution de {numeric[0]}",
                "x_axis": numeric[0], "y_axis": "count", "color": None,
                "rationale": "Voir la distribution"
            })
        
        return proposals[:3]
