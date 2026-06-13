"""
Module : processeur_donnees.py
Description : Traitement des données GPS/IMU .
Projet de Session - MGA802
"""

import numpy as np
import pandas as pd

# =========================================================
#                     GPS
# =========================================================

def preprocess_gps(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # normalisation colonnes
    df.columns = df.columns.str.strip().str.lower()

    # vérification colonnes
    required = ["timestamp", "latitude", "longitude"]
    for c in required:
        if c not in df.columns:
            raise ValueError(f"GPS manquant : {c}")

    # conversion numérique
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    # suppression valeurs invalides
    df = df.dropna(subset=["latitude", "longitude"])

    # filtrage réaliste GPS
    df = df[
        df["latitude"].between(-90, 90) &
        df["longitude"].between(-180, 180)
    ]

    # timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    # radians
    df["latitude_rad"] = np.deg2rad(df["latitude"])
    df["longitude_rad"] = np.deg2rad(df["longitude"])

    print("[OK] GPS prétraité")

    return df


# =========================================================
#                     IMU
# =========================================================

def preprocess_imu(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # normalisation colonnes
    df.columns = df.columns.str.strip().str.lower()

    # mapping automatique (compatible IMUAcquisition)
    mapping = {
        "ax": ["ax", "accx", "acc_x", "acceleration x", "accelerationx", "linear acceleration x"],
        "ay": ["ay", "accy", "acc_y", "acceleration y", "accelerationy", "linear acceleration y"],
        "az": ["az", "accz", "acc_z", "acceleration z", "accelerationz", "linear acceleration z"],
        "gx": ["gx", "gyrox", "gyro x"],
        "gy": ["gy", "gyroy", "gyro y"],
        "gz": ["gz", "gyroz", "gyro z"]
    }

    for target, variants in mapping.items():
        for v in variants:
            if v in df.columns:
                df[target] = df[v]
                break

    required = ["ax", "ay", "az", "gx", "gy", "gz"]

    missing = [c for c in required if c not in df.columns]
    if missing:
        print("[ERROR] Colonnes IMU manquantes :", missing)
        print("[DEBUG] Colonnes disponibles :", list(df.columns))
        raise ValueError("Format IMU incorrect")

    # conversion numérique
    for c in required:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # suppression NaN
    df = df.dropna(subset=required)

    # filtrage bruit (3 sigma)
    for c in ["ax", "ay", "az"]:
        m, s = df[c].mean(), df[c].std()
        df = df[(df[c] > m - 3*s) & (df[c] < m + 3*s)]

    # lissage
    df["ax_f"] = df["ax"].rolling(5, center=True).mean()
    df["ay_f"] = df["ay"].rolling(5, center=True).mean()
    df["az_f"] = df["az"].rolling(5, center=True).mean()

    df[["ax_f", "ay_f", "az_f"]] = df[["ax_f", "ay_f", "az_f"]].bfill()

    # norme accélération
    df["acc_norm"] = np.sqrt(df["ax_f"]**2 + df["ay_f"]**2 + df["az_f"]**2)

    # timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    print("[OK] IMU prétraitée")

    return df


# =========================================================
#                 SYNCHRONISATION
# =========================================================

def synchronize_data(gps: pd.DataFrame, imu: pd.DataFrame):
    """
    Fusion temporelle GPS + IMU
    """

    if imu is None:
        print("[WARN] IMU absente → GPS seul")
        return gps

    gps = gps.sort_values("timestamp")
    imu = imu.sort_values("timestamp")

    merged = pd.merge_asof(
        gps,
        imu,
        on="timestamp",
        direction="nearest",
        tolerance=pd.Timedelta("100ms")
    )

    print("[OK] Synchronisation GPS + IMU réalisée")

    return merged