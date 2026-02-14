"""
Module de validation des données
"""

import pandas as pd
from typing import List, Dict, Tuple, Optional


def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Valide qu'un DataFrame est utilisable pour la visualisation
    
    Args:
        df: DataFrame pandas
        
    Returns:
        Tuple (is_valid, list_of_errors)
    """
    errors = []
    
    # Vérifier que le DataFrame n'est pas vide
    if df.empty:
        errors.append("Le DataFrame est vide")
    
    # Vérifier qu'il y a au moins 2 colonnes
    if len(df.columns) < 2:
        errors.append("Le DataFrame doit contenir au moins 2 colonnes")
    
    # Vérifier qu'il y a au moins 3 lignes
    if len(df) < 3:
        errors.append("Le DataFrame doit contenir au moins 3 lignes de données")
    
    # Vérifier les noms de colonnes dupliqués
    if df.columns.duplicated().any():
        errors.append("Le DataFrame contient des noms de colonnes dupliqués")
    
    # Vérifier si toutes les colonnes sont nulles
    all_null_cols = [col for col in df.columns if df[col].isnull().all()]
    if all_null_cols:
        errors.append(f"Colonnes entièrement nulles: {', '.join(all_null_cols)}")
    
    is_valid = len(errors) == 0
    return is_valid, errors


def check_column_types(df: pd.DataFrame) -> Dict[str, str]:
    """
    Détermine le type de chaque colonne pour la visualisation
    
    Args:
        df: DataFrame pandas
        
    Returns:
        Dictionnaire {nom_colonne: type_viz}
        Types possibles: 'numeric', 'categorical', 'temporal', 'text'
    """
    column_types = {}
    
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            column_types[col] = 'numeric'
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            column_types[col] = 'temporal'
        elif pd.api.types.is_categorical_dtype(df[col]) or df[col].dtype == 'object':
            # Distinguer catégoriel vs texte basé sur le nombre de valeurs uniques
            n_unique = df[col].nunique()
            if n_unique < len(df) * 0.5 and n_unique < 50:
                column_types[col] = 'categorical'
            else:
                column_types[col] = 'text'
        else:
            column_types[col] = 'unknown'
    
    return column_types


def detect_outliers(df: pd.DataFrame, column: str, method: str = 'iqr') -> pd.Series:
    """
    Détecte les outliers dans une colonne numérique
    
    Args:
        df: DataFrame pandas
        column: Nom de la colonne
        method: Méthode de détection ('iqr' ou 'zscore')
        
    Returns:
        Series booléenne indiquant les outliers
    """
    if not pd.api.types.is_numeric_dtype(df[column]):
        raise ValueError(f"La colonne {column} n'est pas numérique")
    
    if method == 'iqr':
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return (df[column] < lower_bound) | (df[column] > upper_bound)
    
    elif method == 'zscore':
        z_scores = (df[column] - df[column].mean()) / df[column].std()
        return abs(z_scores) > 3
    
    else:
        raise ValueError(f"Méthode inconnue: {method}")


def suggest_preprocessing(df: pd.DataFrame) -> List[str]:
    """
    Suggère des étapes de prétraitement pour améliorer la visualisation
    
    Args:
        df: DataFrame pandas
        
    Returns:
        Liste de suggestions
    """
    suggestions = []
    
    # Vérifier les valeurs manquantes
    null_cols = df.columns[df.isnull().any()].tolist()
    if null_cols:
        pct_null = {col: (df[col].isnull().sum() / len(df)) * 100 
                    for col in null_cols}
        high_null = [col for col, pct in pct_null.items() if pct > 50]
        if high_null:
            suggestions.append(
                f"Colonnes avec >50% de valeurs manquantes (considérer la suppression): "
                f"{', '.join(high_null)}"
            )
    
    # Vérifier les colonnes avec une seule valeur unique
    single_value_cols = [col for col in df.columns if df[col].nunique() == 1]
    if single_value_cols:
        suggestions.append(
            f"Colonnes constantes (peu utiles pour la visualisation): "
            f"{', '.join(single_value_cols)}"
        )
    
    # Vérifier les colonnes de texte très longues
    text_cols = df.select_dtypes(include=['object']).columns
    for col in text_cols:
        avg_length = df[col].astype(str).str.len().mean()
        if avg_length > 100:
            suggestions.append(
                f"La colonne '{col}' contient du texte long (moyenne: {avg_length:.0f} caractères)"
            )
    
    return suggestions
