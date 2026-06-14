from __future__ import annotations

import os
from pathlib import Path

import numpy as np
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


def _latlon_to_local_meters(
    latitude_deg: pd.Series,
    longitude_deg: pd.Series,
    altitude_m: pd.Series,
) -> pd.DataFrame:
    """
    Convertit latitude / longitude / altitude en coordonnées locales approximatives
    en mètres, en prenant le premier point GPS comme origine.
    """
    lat_rad = np.deg2rad(latitude_deg.astype(float))
    lon_rad = np.deg2rad(longitude_deg.astype(float))

    lat0 = lat_rad.iloc[0]
    lon0 = lon_rad.iloc[0]
    alt0 = float(altitude_m.iloc[0])

    earth_radius_m = 6371000.0

    x_local_m = (lon_rad - lon0) * np.cos(lat0) * earth_radius_m
    y_local_m = (lat_rad - lat0) * earth_radius_m
    z_local_m = altitude_m.astype(float) - alt0

    return pd.DataFrame({
        "x_local_m": x_local_m,
        "y_local_m": y_local_m,
        "z_local_m": z_local_m,
    })



def _prepare_time_seconds(data: pd.DataFrame) -> pd.Series:
    """
    Convertit la colonne timestamp en secondes relatives.
    """
    if "timestamp" not in data.columns:
        raise ValueError("La colonne 'timestamp' est manquante.")

    time_series = pd.to_datetime(data["timestamp"])
    time_seconds = (time_series - time_series.iloc[0]).dt.total_seconds()
    return time_seconds


def _get_initial_velocity_from_gps(data: pd.DataFrame) -> tuple[float, float]:
    """
    Récupère une vitesse initiale approximative à partir des colonnes GPS
    si elles existent déjà dans le dataset final.
    """
    vx0 = 0.0
    vy0 = 0.0

    if "vitesse est" in data.columns:
        vx0 = float(data["vitesse est"].iloc[0])
    if "vitesse nord" in data.columns:
        vy0 = float(data["vitesse nord"].iloc[0])

    return vx0, vy0


def _rotate_body_acceleration_to_navigation(ax_body: pd.Series, ay_body: pd.Series, yaw_deg: pd.Series | None) -> pd.DataFrame:
    """
    Projette les accélérations IMU du repère corps vers un repère navigation 2D
    à l'aide du yaw si cette information est disponible.
    """
    if yaw_deg is None:
        return pd.DataFrame({
            "ax_nav": ax_body.astype(float),
            "ay_nav": ay_body.astype(float),
        })

    yaw_rad = np.deg2rad(yaw_deg.astype(float))
    cos_yaw = np.cos(yaw_rad)
    sin_yaw = np.sin(yaw_rad)

    ax_nav = cos_yaw * ax_body.astype(float) - sin_yaw * ay_body.astype(float)
    ay_nav = sin_yaw * ax_body.astype(float) + cos_yaw * ay_body.astype(float)

    return pd.DataFrame({
        "ax_nav": ax_nav,
        "ay_nav": ay_nav,
    })


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

    local_coords = _latlon_to_local_meters(
        gps_traj["latitude"],
        gps_traj["longitude"],
        gps_traj["altitude"],
    )

    gps_traj["x_gps"] = local_coords["x_local_m"]
    gps_traj["y_gps"] = local_coords["y_local_m"]
    gps_traj["z_gps"] = local_coords["z_local_m"]

    if "vitesse est" in data.columns:
        gps_traj["vx_gps"] = data["vitesse est"].astype(float)
    if "vitesse nord" in data.columns:
        gps_traj["vy_gps"] = data["vitesse nord"].astype(float)

    output_columns = ["timestamp", "time_s", "x_gps", "y_gps", "z_gps"]
    if "vx_gps" in gps_traj.columns:
        output_columns.append("vx_gps")
    if "vy_gps" in gps_traj.columns:
        output_columns.append("vy_gps")

    return gps_traj[output_columns]


def compute_imu_trajectory(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule une trajectoire IMU simple par double intégration
    à partir des accélérations filtrées ax_f et ay_f.
    """
    required = ["timestamp", "ax_f", "ay_f"]
    missing = [col for col in required if col not in data.columns]
    if missing:
        raise ValueError(f"Colonnes IMU manquantes : {missing}")

    imu_columns = ["timestamp", "ax_f", "ay_f"]
    if "yaw" in data.columns:
        imu_columns.append("yaw")

    imu_traj = data[imu_columns].copy()
    imu_traj["time_s"] = _prepare_time_seconds(imu_traj)

    dt = imu_traj["time_s"].diff().fillna(0.0)
    dt = dt.clip(lower=0.0, upper=1.0)

    imu_traj["ax_f"] = imu_traj["ax_f"].astype(float).interpolate().bfill().ffill()
    imu_traj["ay_f"] = imu_traj["ay_f"].astype(float).interpolate().bfill().ffill()

    if "yaw" in imu_traj.columns:
        imu_traj["yaw"] = imu_traj["yaw"].astype(float).interpolate().bfill().ffill()

    # Suppression d'un biais simple à partir des premières mesures.
    bias_window = min(20, len(imu_traj))
    ax_bias = float(imu_traj["ax_f"].iloc[:bias_window].mean(skipna=True))
    ay_bias = float(imu_traj["ay_f"].iloc[:bias_window].mean(skipna=True))

    imu_traj["ax_corr"] = imu_traj["ax_f"].astype(float) - ax_bias
    imu_traj["ay_corr"] = imu_traj["ay_f"].astype(float) - ay_bias

    # Petit seuil mort pour limiter le bruit résiduel.
    imu_traj.loc[imu_traj["ax_corr"].abs() < 0.03, "ax_corr"] = 0.0
    imu_traj.loc[imu_traj["ay_corr"].abs() < 0.03, "ay_corr"] = 0.0

    yaw_series = imu_traj["yaw"] if "yaw" in imu_traj.columns else None
    nav_acc = _rotate_body_acceleration_to_navigation(
        imu_traj["ax_corr"],
        imu_traj["ay_corr"],
        yaw_series,
    )

    imu_traj["ax_nav"] = nav_acc["ax_nav"]
    imu_traj["ay_nav"] = nav_acc["ay_nav"]

    vx0, vy0 = _get_initial_velocity_from_gps(data)

    vx_values = []
    vy_values = []
    x_values = []
    y_values = []

    current_vx = vx0
    current_vy = vy0
    current_x = 0.0
    current_y = 0.0

    for i in range(len(imu_traj)):
        current_dt = float(dt.iloc[i])
        current_vx += float(imu_traj["ax_nav"].iloc[i]) * current_dt
        current_vy += float(imu_traj["ay_nav"].iloc[i]) * current_dt

        current_x += current_vx * current_dt
        current_y += current_vy * current_dt

        vx_values.append(current_vx)
        vy_values.append(current_vy)
        x_values.append(current_x)
        y_values.append(current_y)

    imu_traj["vx_imu"] = pd.Series(vx_values, index=imu_traj.index).astype(float).interpolate().bfill().ffill()
    imu_traj["vy_imu"] = pd.Series(vy_values, index=imu_traj.index).astype(float).interpolate().bfill().ffill()
    imu_traj["x_imu"] = pd.Series(x_values, index=imu_traj.index).astype(float).interpolate().bfill().ffill()
    imu_traj["y_imu"] = pd.Series(y_values, index=imu_traj.index).astype(float).interpolate().bfill().ffill()

    imu_traj["x_imu"] = imu_traj["x_imu"] - float(imu_traj["x_imu"].iloc[0])
    imu_traj["y_imu"] = imu_traj["y_imu"] - float(imu_traj["y_imu"].iloc[0])

    return imu_traj[["timestamp", "time_s", "x_imu", "y_imu", "vx_imu", "vy_imu"]]


def compute_simple_fusion(
    gps_traj: pd.DataFrame,
    imu_traj: pd.DataFrame,
    alpha: float = 0.7,
) -> pd.DataFrame:
    """
    Fusion GPS/IMU simple de type complémentaire.

    Principe :
    - l'IMU sert à propager la position entre deux instants ;
    - le GPS sert à recaler régulièrement la position ;
    - si les vitesses GPS sont disponibles, elles servent aussi à corriger
      les vitesses IMU.

    `alpha` garde ici le rôle de confiance accordée au GPS :
    - alpha proche de 1 -> correction GPS forte
    - alpha proche de 0 -> confiance plus forte dans la propagation IMU
    """
    merged = pd.merge(gps_traj, imu_traj, on=["timestamp", "time_s"], how="inner")
    merged = merged.sort_values("time_s").reset_index(drop=True)

    merged["x_imu"] = merged["x_imu"].astype(float).interpolate().bfill().ffill()
    merged["y_imu"] = merged["y_imu"].astype(float).interpolate().bfill().ffill()
    merged["vx_imu"] = merged["vx_imu"].astype(float).interpolate().bfill().ffill()
    merged["vy_imu"] = merged["vy_imu"].astype(float).interpolate().bfill().ffill()
    merged["x_gps"] = merged["x_gps"].astype(float).interpolate().bfill().ffill()
    merged["y_gps"] = merged["y_gps"].astype(float).interpolate().bfill().ffill()

    has_gps_velocity = "vx_gps" in merged.columns and "vy_gps" in merged.columns
    if has_gps_velocity:
        merged["vx_gps"] = merged["vx_gps"].astype(float).interpolate().bfill().ffill()
        merged["vy_gps"] = merged["vy_gps"].astype(float).interpolate().bfill().ffill()

    # Gains de correction : position plus fortement corrigée que la vitesse.
    pos_gain = float(alpha)
    vel_gain = min(float(alpha), 0.5)

    x_fused_values = []
    y_fused_values = []
    vx_fused_values = []
    vy_fused_values = []

    x_prev = float(merged.loc[0, "x_gps"])
    y_prev = float(merged.loc[0, "y_gps"])

    if has_gps_velocity:
        vx_prev = float(merged.loc[0, "vx_gps"])
        vy_prev = float(merged.loc[0, "vy_gps"])
    else:
        vx_prev = float(merged.loc[0, "vx_imu"])
        vy_prev = float(merged.loc[0, "vy_imu"])

    x_fused_values.append(x_prev)
    y_fused_values.append(y_prev)
    vx_fused_values.append(vx_prev)
    vy_fused_values.append(vy_prev)

    for i in range(1, len(merged)):
        dt = float(merged.loc[i, "time_s"] - merged.loc[i - 1, "time_s"])
        dt = max(0.0, min(dt, 1.0))

        # Propagation par l'IMU sous forme d'incrément de déplacement.
        delta_x_imu = float(merged.loc[i, "x_imu"] - merged.loc[i - 1, "x_imu"])
        delta_y_imu = float(merged.loc[i, "y_imu"] - merged.loc[i - 1, "y_imu"])

        x_pred = x_prev + delta_x_imu
        y_pred = y_prev + delta_y_imu
        vx_pred = float(merged.loc[i, "vx_imu"])
        vy_pred = float(merged.loc[i, "vy_imu"])

        # Recalage par le GPS à chaque pas disponible.
        x_gps = float(merged.loc[i, "x_gps"])
        y_gps = float(merged.loc[i, "y_gps"])

        x_corr = x_pred + pos_gain * (x_gps - x_pred)
        y_corr = y_pred + pos_gain * (y_gps - y_pred)

        if has_gps_velocity:
            vx_gps = float(merged.loc[i, "vx_gps"])
            vy_gps = float(merged.loc[i, "vy_gps"])
            vx_corr = vx_pred + vel_gain * (vx_gps - vx_pred)
            vy_corr = vy_pred + vel_gain * (vy_gps - vy_pred)
        else:
            vx_corr = vx_pred
            vy_corr = vy_pred

        x_fused_values.append(x_corr)
        y_fused_values.append(y_corr)
        vx_fused_values.append(vx_corr)
        vy_fused_values.append(vy_corr)

        x_prev = x_corr
        y_prev = y_corr
        vx_prev = vx_corr
        vy_prev = vy_corr

    merged["x_fused"] = pd.Series(x_fused_values, index=merged.index)
    merged["y_fused"] = pd.Series(y_fused_values, index=merged.index)
    merged["vx_fused"] = pd.Series(vx_fused_values, index=merged.index)
    merged["vy_fused"] = pd.Series(vy_fused_values, index=merged.index)

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


"""
Charge le dataset final, calcule les trajectoires GPS / IMU / fusionnées
et retourne le DataFrame final.
"""
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
