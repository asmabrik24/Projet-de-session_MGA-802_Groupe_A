import numpy as np
import pandas as pd


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
    required = [x_est_col, y_est_col, x_ref_col, y_ref_col]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes pour le calcul d'erreur : {missing}")

    out = df.copy()

    out[f"{prefix}_x"] = out[x_est_col] - out[x_ref_col]
    out[f"{prefix}_y"] = out[y_est_col] - out[y_ref_col]
    out[f"{prefix}_2d"] = np.sqrt(out[f"{prefix}_x"] ** 2 + out[f"{prefix}_y"] ** 2)

    if z_est_col is not None and z_est_col in out.columns and z_ref_col in out.columns:
        out[f"{prefix}_z"] = out[z_est_col] - out[z_ref_col]
        out[f"{prefix}_3d"] = np.sqrt(
            out[f"{prefix}_x"] ** 2 + out[f"{prefix}_y"] ** 2 + out[f"{prefix}_z"] ** 2
        )

    return out


def compute_rmse(series: pd.Series) -> float:
    """
    Calcule le RMSE d'une série d'erreurs.
    """
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        raise ValueError("Impossible de calculer le RMSE sur une série vide.")
    return float(np.sqrt(np.mean(clean**2)))


def summarize_error_statistics(
    df: pd.DataFrame,
    err_2d_col: str,
    err_3d_col: str | None = None,
) -> pd.DataFrame:
    """
    Retourne un petit tableau de statistiques d'erreur.
    """
    if err_2d_col not in df.columns:
        raise ValueError(f"Colonne absente : {err_2d_col}")

    summary = {
        "Erreur 2D moyenne": float(df[err_2d_col].mean()),
        "Erreur 2D RMS": compute_rmse(df[err_2d_col]),
        "Erreur 2D maximale": float(df[err_2d_col].max()),
    }

    if err_3d_col is not None and err_3d_col in df.columns:
        summary["Erreur 3D moyenne"] = float(df[err_3d_col].mean())
        summary["Erreur 3D RMS"] = compute_rmse(df[err_3d_col])

    return pd.DataFrame(
        {
            "Paramètre": list(summary.keys()),
            "Valeur": list(summary.values()),
        }
    )