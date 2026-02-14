"""
Module d'exécution de code de visualisation
Exécute le code généré par le LLM de manière sécurisée
"""

import pandas as pd
import plotly.graph_objects as go
from typing import Optional, Dict, Any
import sys
from io import StringIO


class VisualizationPlotter:
    """Classe pour exécuter et générer des visualisations"""
    
    def __init__(self):
        """Initialise le plotter"""
        pass
    
    def execute_plot_code(
        self,
        code: str,
        df: pd.DataFrame
    ) -> Optional[go.Figure]:
        """
        Exécute le code de visualisation de manière contrôlée
        
        Args:
            code: Code Python à exécuter
            df: DataFrame pandas
            
        Returns:
            Figure Plotly ou None si erreur
        """
        try:
            # Créer un namespace isolé pour l'exécution
            namespace = {
                'pd': pd,
                'go': go,
                'df': df,
                '__builtins__': __builtins__
            }
            
            # Capturer stdout/stderr pour éviter les prints
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = StringIO()
            sys.stderr = StringIO()
            
            try:
                # Exécuter le code
                exec(code, namespace)
                
                # Vérifier que create_figure existe
                if 'create_figure' not in namespace:
                    raise ValueError("Le code doit définir une fonction create_figure(df)")
                
                # Appeler la fonction
                fig = namespace['create_figure'](df)
                
                # Vérifier que c'est bien une Figure Plotly
                if not isinstance(fig, go.Figure):
                    raise ValueError(
                        f"create_figure doit retourner un plotly.graph_objects.Figure, "
                        f"reçu {type(fig)}"
                    )
                
                return fig
                
            finally:
                # Restaurer stdout/stderr
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                
        except Exception as e:
            print(f"Erreur lors de l'exécution du code: {str(e)}")
            return None
    
    def create_fallback_visualization(
        self,
        df: pd.DataFrame,
        x_col: str,
        y_col: str,
        title: str = "Visualisation"
    ) -> go.Figure:
        """
        Crée une visualisation de secours simple en cas d'erreur
        
        Args:
            df: DataFrame pandas
            x_col: Nom de la colonne X
            y_col: Nom de la colonne Y
            title: Titre du graphique
            
        Returns:
            Figure Plotly simple
        """
        try:
            # Nettoyer les données
            df_clean = df[[x_col, y_col]].dropna()
            
            # Déterminer le type de graphique selon les types de données
            if pd.api.types.is_numeric_dtype(df[x_col]) and pd.api.types.is_numeric_dtype(df[y_col]):
                # Scatter plot pour numérique vs numérique
                fig = go.Figure(data=go.Scatter(
                    x=df_clean[x_col],
                    y=df_clean[y_col],
                    mode='markers',
                    marker=dict(color='steelblue', size=8, opacity=0.6)
                ))
            else:
                # Bar chart par défaut
                if pd.api.types.is_numeric_dtype(df[y_col]):
                    # Grouper si nécessaire
                    if len(df_clean) > 50:
                        df_agg = df_clean.groupby(x_col)[y_col].mean().reset_index()
                    else:
                        df_agg = df_clean
                    
                    fig = go.Figure(data=go.Bar(
                        x=df_agg[x_col],
                        y=df_agg[y_col],
                        marker_color='steelblue'
                    ))
                else:
                    # Compter les occurrences
                    counts = df_clean[x_col].value_counts()
                    fig = go.Figure(data=go.Bar(
                        x=counts.index,
                        y=counts.values,
                        marker_color='steelblue'
                    ))
            
            # Configuration du layout
            fig.update_layout(
                title={
                    'text': title,
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 18}
                },
                xaxis_title=x_col,
                yaxis_title=y_col,
                font={'size': 12},
                template='plotly_white',
                showlegend=False,
                hovermode='closest'
            )
            
            return fig
            
        except Exception as e:
            # Dernier recours: graphique vide avec message d'erreur
            fig = go.Figure()
            fig.add_annotation(
                text=f"Impossible de créer la visualisation:<br>{str(e)}",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=14)
            )
            fig.update_layout(
                title="Erreur de visualisation",
                template='plotly_white'
            )
            return fig
    
    def validate_figure(self, fig: go.Figure) -> tuple[bool, str]:
        """
        Valide qu'une figure est correcte et complète
        
        Args:
            fig: Figure Plotly
            
        Returns:
            Tuple (is_valid, error_message)
        """
        if fig is None:
            return False, "La figure est None"
        
        if not isinstance(fig, go.Figure):
            return False, f"Type incorrect: {type(fig)}"
        
        # Vérifier qu'il y a des données
        if not fig.data:
            return False, "La figure ne contient pas de données"
        
        # Vérifier qu'il y a un titre
        if not fig.layout.title or not fig.layout.title.text:
            return False, "La figure n'a pas de titre"
        
        return True, ""
