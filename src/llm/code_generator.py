"""
Génération de code Plotly via Ollama Mistral
"""

import requests
import re
from typing import Dict, Any


class CodeGenerator:
    """Générateur de code avec Mistral local"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "mistral-opt"
    
    def generate_plot_code(self, proposal: Dict[str, Any], df_info: Dict[str, Any]) -> str:
        """Génère le code Plotly"""
        
        viz_type = proposal.get('type', 'bar_chart')
        title = proposal.get('title', 'Visualisation')
        x_axis = proposal.get('x_axis')
        y_axis = proposal.get('y_axis')
        
        # Pour les cas simples, utiliser directement le fallback
        if y_axis == 'count' or viz_type == 'histogram':
            return self._get_histogram_code(x_axis, title)
        
        # Détecter si besoin d'agrégation
        categorical_cols = df_info.get('categorical_columns', [])
        if x_axis in categorical_cols and y_axis != 'count':
            return self._get_aggregation_code(x_axis, y_axis, title, viz_type)
        
        # Essayer avec Mistral
        prompt = f"""Génère du code Python avec Plotly.

TYPE: {viz_type}
TITRE: {title}
X: {x_axis}
Y: {y_axis}

Code requis:
- Fonction create_figure(df) qui retourne une figure Plotly
- Import plotly.graph_objects as go
- Gère les valeurs manquantes avec dropna()

Réponds UNIQUEMENT avec le code Python, sans markdown."""
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=30
            )
            content = response.json()["response"]
            code = self._extract_code(content)
            return code
        except:
            return self._get_default_code(x_axis, y_axis, title, viz_type)
    
    def _extract_code(self, content: str) -> str:
        """Extrait le code Python"""
        content = re.sub(r'```python\n?', '', content)
        content = re.sub(r'```\n?', '', content)
        return content.strip()
    
    def _get_histogram_code(self, x: str, title: str) -> str:
        """Code pour un histogram"""
        return f'''import plotly.graph_objects as go

def create_figure(df):
    df_clean = df[['{x}']].dropna()
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=df_clean['{x}']))
    
    fig.update_layout(
        title='{title}',
        xaxis_title='{x}',
        yaxis_title='Count',
        template='plotly_white'
    )
    return fig
'''
    
    def _get_aggregation_code(self, x: str, y: str, title: str, viz_type: str) -> str:
        """Code pour agrégation (moyenne par catégorie)"""
        trace_type = "Bar" if viz_type == "bar_chart" else "Scatter"
        
        return f'''import plotly.graph_objects as go

def create_figure(df):
    # Agrégation: moyenne de {y} par {x}
    df_agg = df.groupby('{x}')['{y}'].mean().reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.{trace_type}(
        x=df_agg['{x}'], 
        y=df_agg['{y}'],
        marker_color='steelblue'
    ))
    
    fig.update_layout(
        title='{title}',
        xaxis_title='{x}',
        yaxis_title='Moyenne de {y}',
        template='plotly_white'
    )
    return fig
'''
    
    def _get_default_code(self, x: str, y: str, title: str, viz_type: str) -> str:
        """Code par défaut"""
        if viz_type == 'scatter_plot':
            trace = f"go.Scatter(x=df_clean['{x}'], y=df_clean['{y}'], mode='markers')"
        else:
            trace = f"go.Bar(x=df_clean['{x}'], y=df_clean['{y}'])"
        
        return f'''import plotly.graph_objects as go

def create_figure(df):
    df_clean = df[['{x}', '{y}']].dropna()
    
    fig = go.Figure()
    fig.add_trace({trace})
    
    fig.update_layout(
        title='{title}',
        xaxis_title='{x}',
        yaxis_title='{y}',
        template='plotly_white'
    )
    return fig
'''
