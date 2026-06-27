import numpy as np
import pandas as pd

# Module de calcul des métriques d'erreur.
# Il fournit les fonctions utiles pour comparer une trajectoire estimée
# à une référence GPS et produire des statistiques synthétiques.

# Calcule les erreurs de position élémentaires et les normes 2D/3D associées.
def compute_position_errors(
    df: pd.DataFrame,
    x_est_col: str,
    y_est_col: str,
    z_est_col: str | None = None,
    x_ref_col: str = "x_gps",
    y_ref_col: str = "y_gps",
    z_ref_col: str = "z_gps",
    prefix: str = "err",
) -> pd.DataFrame:
    """
    Calcule les erreurs de position entre une estimation et la référence GPS.
    """
    # Vérifie que les colonnes minimales nécessaires au calcul 2D sont présentes.
    required = [x_est_col, y_est_col, x_ref_col, y_ref_col]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes pour le calcul d'erreur : {missing}")

    # Copie défensive pour préserver le DataFrame d'origine.
    out = df.copy()

    # Calcul des écarts élémentaires et de la norme d'erreur plane.
    out[f"{prefix}_x"] = out[x_est_col] - out[x_ref_col]
    out[f"{prefix}_y"] = out[y_est_col] - out[y_ref_col]
    out[f"{prefix}_2d"] = np.sqrt(out[f"{prefix}_x"] ** 2 + out[f"{prefix}_y"] ** 2)

    # Si les composantes verticales existent, calcule aussi l'erreur 3D.
    if z_est_col is not None and z_est_col in out.columns and z_ref_col in out.columns:
        out[f"{prefix}_z"] = out[z_est_col] - out[z_ref_col]
        out[f"{prefix}_3d"] = np.sqrt(
            out[f"{prefix}_x"] ** 2 + out[f"{prefix}_y"] ** 2 + out[f"{prefix}_z"] ** 2
        )

    return out


# Calcule la racine de l'erreur quadratique moyenne à partir d'une série numérique.
def compute_rmse(series: pd.Series) -> float:
    """
    Calcule le RMSE d'une série d'erreurs.
    """
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return float("nan")
    return float(np.sqrt(np.mean(clean**2)))


# Construit un tableau récapitulatif des erreurs moyennes, RMS et maximales.
def summarize_error_statistics(
    df: pd.DataFrame,
    err_2d_col: str,
    err_3d_col: str | None = None,
) -> pd.DataFrame:
    """
    Retourne un petit tableau de statistiques d'erreur.
    Gère proprement le cas d'un DataFrame vide.
    """
    # La colonne d'erreur 2D est obligatoire pour construire le résumé.
    if err_2d_col not in df.columns:
        raise ValueError(f"Colonne absente : {err_2d_col}")

    # Nettoyage numérique pour ignorer les valeurs manquantes ou invalides.
    clean_2d = pd.to_numeric(df[err_2d_col], errors="coerce").dropna()

    # Si aucune donnée exploitable n'est disponible, retourne des NaN plutôt qu'une erreur.
    if clean_2d.empty:
        summary = {
            "Erreur 2D moyenne": float("nan"),
            "Erreur 2D RMS": float("nan"),
            "Erreur 2D maximale": float("nan"),
        }
    else:
        summary = {
            "Erreur 2D moyenne": float(clean_2d.mean()),
            "Erreur 2D RMS": compute_rmse(clean_2d),
            "Erreur 2D maximale": float(clean_2d.max()),
        }

    # Ajoute les statistiques 3D uniquement si la colonne correspondante est disponible.
    if err_3d_col is not None and err_3d_col in df.columns:
        clean_3d = pd.to_numeric(df[err_3d_col], errors="coerce").dropna()
        if clean_3d.empty:
            summary["Erreur 3D moyenne"] = float("nan")
            summary["Erreur 3D RMS"] = float("nan")
        else:
            summary["Erreur 3D moyenne"] = float(clean_3d.mean())
            summary["Erreur 3D RMS"] = compute_rmse(clean_3d)

    return pd.DataFrame(
        {
            "Paramètre": list(summary.keys()),
            "Valeur": list(summary.values()),
        }
    )