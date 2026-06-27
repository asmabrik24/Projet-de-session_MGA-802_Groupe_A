"""
Module : pre_traitement.py
Description : Prétraitement et synchronisation des données GPS/IMU.
Projet de Session - MGA802
"""

import numpy as np
import pandas as pd

# Module de prétraitement des données GPS/IMU.
# Il prépare les jeux de données bruts avant la navigation :
# nettoyage, conversion, filtrage, lissage et synchronisation temporelle.

# =========================================================
#                     GPS
# =========================================================

# Nettoie les données GPS, valide les colonnes utiles et prépare des champs dérivés en radians.
def preprocess_gps(df: pd.DataFrame) -> pd.DataFrame:
    """Prépare un DataFrame GPS propre et ordonné temporellement."""
    # Copie défensive pour éviter de modifier le DataFrame d'origine.
    df = df.copy()

    # normalisation colonnes
    df.columns = df.columns.str.strip().str.lower()

    # vérification colonnes
    required = ["timestamp", "latitude", "longitude"]
    for c in required:
        if c not in df.columns:
            raise ValueError(f"GPS manquant : {c}")

    # Conversion explicite des coordonnées GPS pour filtrer les valeurs invalides.
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

    # Mise au format temporel et tri chronologique des échantillons.
    # timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    # Préparation des coordonnées en radians pour les calculs ultérieurs.
    # radians
    df["latitude_rad"] = np.deg2rad(df["latitude"])
    df["longitude_rad"] = np.deg2rad(df["longitude"])

    print("[OK] GPS prétraité")

    return df


# =========================================================
#                     IMU
# =========================================================

# Nettoie les données IMU, harmonise les colonnes capteur et calcule les signaux filtrés.
def preprocess_imu(df: pd.DataFrame) -> pd.DataFrame:
    """Prépare un DataFrame IMU propre avec accélérations filtrées et norme associée."""
    # Copie défensive pour éviter de modifier le DataFrame d'origine.
    df = df.copy()

    # normalisation colonnes
    df.columns = df.columns.str.lower()

    df = df.rename(columns={
        "accel_x": "ax",
        "accel_y": "ay",
        "accel_z": "az",
        "gyro_x": "gx",
        "gyro_y": "gy",
        "gyro_z": "gz"
    })

    # Harmonisation initiale des noms de colonnes les plus fréquents.
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

    # Conversion explicite des mesures IMU pour nettoyer les entrées non numériques.
    # conversion numérique
    for c in required:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Suppression des lignes inexploitables après conversion.
    # suppression NaN
    df = df.dropna(subset=required)

    # Réduction des valeurs aberrantes sur les accélérations via un filtrage 3 sigma.
    # filtrage bruit (3 sigma)
    for c in ["ax", "ay", "az"]:
        m, s = df[c].mean(), df[c].std()
        df = df[(df[c] > m - 3*s) & (df[c] < m + 3*s)]

    # Lissage glissant pour réduire le bruit avant intégration/navigation.
    # lissage
    df["ax_f"] = df["ax"].rolling(5, center=True).mean()
    df["ay_f"] = df["ay"].rolling(5, center=True).mean()
    df["az_f"] = df["az"].rolling(5, center=True).mean()

    df[["ax_f", "ay_f", "az_f"]] = df[["ax_f", "ay_f", "az_f"]].bfill()

    # Calcul d'une grandeur synthétique utile pour l'analyse de mouvement.
    # norme accélération
    df["acc_norm"] = np.sqrt(df["ax_f"]**2 + df["ay_f"]**2 + df["az_f"]**2)

    # Mise au format temporel et tri chronologique des mesures IMU.
    # timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    print("[OK] IMU prétraitée")

    return df


# =========================================================
#                 SYNCHRONISATION
# =========================================================

# Synchronise les données GPS et IMU à partir du timestamp le plus proche.
def synchronize_data(gps: pd.DataFrame, imu: pd.DataFrame):
    """
    Fusion temporelle GPS + IMU
    """
    # Si aucune IMU n'est disponible, on conserve uniquement les données GPS.
    if imu is None:
        print("[WARN] IMU absente → GPS seul")
        return gps

    gps = gps.sort_values("timestamp")
    imu = imu.sort_values("timestamp")

    # Association de chaque échantillon GPS avec la mesure IMU la plus proche dans le temps.
    merged = pd.merge_asof(
        gps,
        imu,
        on="timestamp",
        direction="nearest",
        tolerance=pd.Timedelta("100ms")
    )

    print("[OK] Synchronisation GPS + IMU réalisée")

    return merged