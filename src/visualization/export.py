"""
Module d'export de visualisations
Permet d'exporter les figures en PNG haute qualité
"""

import plotly.graph_objects as go
from pathlib import Path
from typing import Optional
import tempfile


def export_figure_to_png(
    fig: go.Figure,
    filename: str = "visualization.png",
    width: int = 1200,
    height: int = 800,
    scale: float = 2.0
) -> Optional[str]:
    """
    Exporte une figure Plotly en PNG
    
    Args:
        fig: Figure Plotly à exporter
        filename: Nom du fichier de sortie
        width: Largeur en pixels
        height: Hauteur en pixels
        scale: Facteur d'échelle pour la qualité (2.0 = haute qualité)
        
    Returns:
        Chemin du fichier généré ou None si erreur
    """
    try:
        # Créer un répertoire temporaire si nécessaire
        temp_dir = Path(tempfile.gettempdir()) / "dataviz_exports"
        temp_dir.mkdir(exist_ok=True)
        
        # Chemin complet du fichier
        filepath = temp_dir / filename
        
        # Exporter en PNG avec kaleido
        fig.write_image(
            str(filepath),
            format='png',
            width=width,
            height=height,
            scale=scale
        )
        
        return str(filepath)
        
    except Exception as e:
        print(f"Erreur lors de l'export PNG: {str(e)}")
        return None


def export_figure_to_bytes(
    fig: go.Figure,
    width: int = 1200,
    height: int = 800,
    scale: float = 2.0
) -> Optional[bytes]:
    """
    Exporte une figure Plotly en bytes PNG
    Utile pour Streamlit download_button
    
    Args:
        fig: Figure Plotly à exporter
        width: Largeur en pixels
        height: Hauteur en pixels
        scale: Facteur d'échelle pour la qualité
        
    Returns:
        Bytes du PNG ou None si erreur
    """
    try:
        # Exporter en bytes
        img_bytes = fig.to_image(
            format='png',
            width=width,
            height=height,
            scale=scale
        )
        
        return img_bytes
        
    except Exception as e:
        print(f"Erreur lors de l'export en bytes: {str(e)}")
        return None


def get_export_formats() -> list[str]:
    """
    Retourne la liste des formats d'export supportés
    
    Returns:
        Liste des formats disponibles
    """
    return ['png', 'jpeg', 'svg', 'pdf']


def export_figure_multi_format(
    fig: go.Figure,
    base_filename: str = "visualization",
    formats: list[str] = None,
    output_dir: Optional[Path] = None
) -> dict[str, str]:
    """
    Exporte une figure dans plusieurs formats
    
    Args:
        fig: Figure Plotly
        base_filename: Nom de base (sans extension)
        formats: Liste de formats à générer (défaut: ['png'])
        output_dir: Répertoire de sortie (défaut: temp)
        
    Returns:
        Dictionnaire {format: filepath}
    """
    if formats is None:
        formats = ['png']
    
    if output_dir is None:
        output_dir = Path(tempfile.gettempdir()) / "dataviz_exports"
    
    output_dir.mkdir(exist_ok=True)
    
    exported = {}
    
    for fmt in formats:
        try:
            filename = f"{base_filename}.{fmt}"
            filepath = output_dir / filename
            
            fig.write_image(
                str(filepath),
                format=fmt,
                width=1200,
                height=800,
                scale=2.0
            )
            
            exported[fmt] = str(filepath)
            
        except Exception as e:
            print(f"Erreur export {fmt}: {str(e)}")
            continue
    
    return exported
