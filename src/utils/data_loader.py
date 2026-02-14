"""
Module de chargement et d'analyse des données CSV
"""

import pandas as pd
from typing import Dict, Any, Optional
import io


def load_csv(file_content: Any, encoding: str = "utf-8") -> pd.DataFrame:
    """
    Charge un fichier CSV en DataFrame pandas
    
    Args:
        file_content: Contenu du fichier (bytes ou file-like object)
        encoding: Encodage du fichier
        
    Returns:
        DataFrame pandas
        
    Raises:
        ValueError: Si le fichier ne peut pas être lu
    """
    try:
        # Si c'est un objet UploadedFile de Streamlit
        if hasattr(file_content, 'getvalue'):
            content = file_content.getvalue()
            df = pd.read_csv(io.BytesIO(content), encoding=encoding)
        else:
            df = pd.read_csv(file_content, encoding=encoding)
        
        return df
    except UnicodeDecodeError:
        # Essayer avec un autre encodage
        try:
            if hasattr(file_content, 'seek'):
                file_content.seek(0)
            df = pd.read_csv(file_content, encoding='latin-1')
            return df
        except Exception as e:
            raise ValueError(f"Impossible de lire le fichier CSV: {str(e)}")
    except Exception as e:
        raise ValueError(f"Erreur lors du chargement du CSV: {str(e)}")


def get_dataframe_info(df: pd.DataFrame, n_rows: int = 5) -> Dict[str, Any]:
    """
    Extrait les informations importantes d'un DataFrame
    
    Args:
        df: DataFrame pandas
        n_rows: Nombre de lignes à inclure dans l'aperçu
        
    Returns:
        Dictionnaire contenant les métadonnées du DataFrame
    """
    info = {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "null_counts": df.isnull().sum().to_dict(),
        "head": df.head(n_rows).to_dict(orient='records'),
        "numeric_columns": list(df.select_dtypes(include=['number']).columns),
        "categorical_columns": list(df.select_dtypes(include=['object', 'category']).columns),
        "datetime_columns": list(df.select_dtypes(include=['datetime64']).columns),
    }
    
    # Statistiques descriptives pour les colonnes numériques
    if len(info["numeric_columns"]) > 0:
        info["numeric_stats"] = df[info["numeric_columns"]].describe().to_dict()
    
    return info


def infer_column_semantics(df: pd.DataFrame) -> Dict[str, str]:
    """
    Infère le rôle sémantique de chaque colonne
    
    Args:
        df: DataFrame pandas
        
    Returns:
        Dictionnaire {nom_colonne: type_sémantique}
    """
    semantics = {}
    
    for col in df.columns:
        dtype = df[col].dtype
        
        # Détection de dates
        if pd.api.types.is_datetime64_any_dtype(dtype):
            semantics[col] = "temporal"
        # Détection de numériques
        elif pd.api.types.is_numeric_dtype(dtype):
            # Vérifier si c'est potentiellement un ID
            if df[col].nunique() == len(df) and col.lower() in ['id', 'index', 'key']:
                semantics[col] = "identifier"
            else:
                semantics[col] = "quantitative"
        # Détection de catégories
        elif pd.api.types.is_object_dtype(dtype):
            n_unique = df[col].nunique()
            # Si peu de valeurs uniques, c'est probablement catégoriel
            if n_unique < len(df) * 0.5:
                semantics[col] = "categorical"
            else:
                semantics[col] = "text"
        else:
            semantics[col] = "unknown"
    
    return semantics
