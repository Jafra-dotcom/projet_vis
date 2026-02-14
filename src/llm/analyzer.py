"""
Analyse de problématique via Ollama Mistral (Local)
"""

import requests
import pandas as pd
import json
from typing import Dict, Any


class DataVizAnalyzer:
    """Analyseur avec Ollama Mistral local"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "mistral"
    
    def analyze_question(self, question: str, df: pd.DataFrame, df_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse la question avec Mistral local"""
        
        prompt = f"""Analyse cette problématique et ce dataset.

PROBLÉMATIQUE: "{question}"

COLONNES:
Numériques: {', '.join(df_info.get('numeric_columns', []))}
Catégorielles: {', '.join(df_info.get('categorical_columns', []))}

Réponds en JSON uniquement:
{{
  "analytical_goal": "comparison ou trend_analysis ou distribution ou correlation",
  "key_variables": ["var1", "var2"],
  "suggested_focus": "Description courte"
}}"""
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=30
            )
            content = response.json()["response"]
            
            # Extraire le JSON de la réponse
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                content = content[start:end]
            
            return json.loads(content)
        except:
            return {
                "analytical_goal": "exploration",
                "key_variables": df_info["columns"][:3],
                "suggested_focus": "Analyse exploratoire"
            }
