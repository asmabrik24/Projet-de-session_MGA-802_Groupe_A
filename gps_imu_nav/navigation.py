from __future__ import annotations

import os
from pathlib import Path

import pandas as pd


DEFAULT_NAVIGATION_OUTPUT_NAME = "navigation_outputs.pkl"
DEFAULT_DATASET_NAME = "dataset_final.pkl"
DEFAULT_DATA_DIR_NAME = "données"


def get_project_root() -> Path:
    """Retourne la racine du projet à partir du dossier du module."""
    return Path(__file__).resolve().parent.parent


def get_data_dir() -> Path:
    """Retourne le dossier des données du projet."""
    return get_project_root() / DEFAULT_DATA_DIR_NAME


def get_default_dataset_path() -> Path:
    """Retourne le chemin par défaut du dataset synchronisé."""
    return get_data_dir() / DEFAULT_DATASET_NAME


def load_navigation_dataset(dataset_path: str | os.PathLike | None = None) -> pd.DataFrame:
    """
    Charge le dataset final au format Pickle.

    Si aucun chemin n'est fourni, le script cherche automatiquement
    `données/dataset_final.pkl` à la racine du projet.
    """
    path = Path(dataset_path) if dataset_path is not None else get_default_dataset_path()

    if not path.exists():
        raise FileNotFoundError(f"Dataset final introuvable : {path}")

    return pd.read_pickle(path)


def _prepare_time_seconds(data: pd.DataFrame) -> pd.Series:
    """
    Convertit la colonne timestamp en secondes relatives.
    """
    if "timestamp" not in data.columns:
        raise ValueError("La colonne 'timestamp' est manquante.")

    time_series = pd.to_datetime(data["timestamp"])
    time_seconds = (time_series - time_series.iloc[0]).dt.total_seconds()
    return time_seconds


def compute_gps_trajectory(data: pd.DataFrame) -> pd.DataFrame:
    """
    Extrait la trajectoire GPS seule à partir du dataset final.
    """
    required = ["timestamp", "latitude", "longitude", "altitude"]
    missing = [col for col in required if col not in data.columns]
    if missing:
        raise ValueError(f"Colonnes GPS manquantes : {missing}")

    gps_traj = data[required].copy()
    gps_traj["time_s"] = _prepare_time_seconds(gps_traj)

    gps_traj = gps_traj.rename(columns={
        "latitude": "x_gps",
        "longitude": "y_gps",
        "altitude": "z_gps",
    })

    return gps_traj[["timestamp", "time_s", "x_gps", "y_gps", "z_gps"]]


def compute_imu_trajectory(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule une trajectoire IMU simple par double intégration
    à partir des accélérations filtrées ax_f et ay_f.
    """
    required = ["timestamp", "ax_f", "ay_f"]
    missing = [col for col in required if col not in data.columns]
    if missing:
        raise ValueError(f"Colonnes IMU manquantes : {missing}")

    imu_traj = data[required].copy()
    imu_traj["time_s"] = _prepare_time_seconds(imu_traj)

    dt = imu_traj["time_s"].diff().fillna(0.0)

    imu_traj["vx_imu"] = (imu_traj["ax_f"] * dt).cumsum()
    imu_traj["vy_imu"] = (imu_traj["ay_f"] * dt).cumsum()

    imu_traj["x_imu"] = (imu_traj["vx_imu"] * dt).cumsum()
    imu_traj["y_imu"] = (imu_traj["vy_imu"] * dt).cumsum()

    return imu_traj[["timestamp", "time_s", "x_imu", "y_imu", "vx_imu", "vy_imu"]]


def compute_simple_fusion(
    gps_traj: pd.DataFrame,
    imu_traj: pd.DataFrame,
    alpha: float = 0.7,
) -> pd.DataFrame:
    """
    Fusion simple GPS/IMU par combinaison pondérée.
    alpha proche de 1 -> plus de poids au GPS
    alpha proche de 0 -> plus de poids à l'IMU
    """
    merged = pd.merge(gps_traj, imu_traj, on=["timestamp", "time_s"], how="inner")

    merged["x_fused"] = alpha * merged["x_gps"] + (1 - alpha) * merged["x_imu"]
    merged["y_fused"] = alpha * merged["y_gps"] + (1 - alpha) * merged["y_imu"]

    return merged


def build_navigation_outputs(data: pd.DataFrame, alpha: float = 0.7) -> pd.DataFrame:
    """
    Retourne un DataFrame global contenant :
    - trajectoire GPS
    - trajectoire IMU
    - trajectoire fusionnée
    """
    gps_traj = compute_gps_trajectory(data)
    imu_traj = compute_imu_trajectory(data)
    fused_traj = compute_simple_fusion(gps_traj, imu_traj, alpha=alpha)

    return fused_traj


def run_navigation(
    dataset_path: str | os.PathLike | None = None,
    alpha: float = 0.7,
    save_output: bool = False,
    output_path: str | os.PathLike | None = None,
) -> pd.DataFrame:
    """
    Charge le dataset final, calcule les trajectoires GPS / IMU / fusionnées
    et retourne le DataFrame final.
    """
    data = load_navigation_dataset(dataset_path)
    navigation_outputs = build_navigation_outputs(data, alpha=alpha)

    if save_output:
        final_output_path = Path(output_path) if output_path is not None else get_data_dir() / DEFAULT_NAVIGATION_OUTPUT_NAME
        navigation_outputs.to_pickle(final_output_path)

    return navigation_outputs
