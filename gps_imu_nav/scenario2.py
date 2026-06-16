import pandas as pd


def simulate_gps_outage(
    navigation_results: pd.DataFrame,
    outage_start_s: float = 30.0,
) -> pd.DataFrame:
    """
    Simule une panne GPS à partir d'un instant donné.

    Avant outage_start_s :
        - on garde la trajectoire fusionnée comme estimation principale

    Après outage_start_s :
        - on passe en mode IMU seul (dead reckoning)

    Retourne un DataFrame enrichi avec :
        - gps_available
        - x_s2, y_s2
        - mode_s2
        - t_outage
    """
    required = [
        "time_s",
        "x_gps",
        "y_gps",
        "x_fused",
        "y_fused",
        "x_imu",
        "y_imu",
    ]
    missing = [col for col in required if col not in navigation_results.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes pour le scénario 2 : {missing}")

    df = navigation_results.copy()
    df = df.sort_values("time_s").reset_index(drop=True)

    df["gps_available"] = df["time_s"] < outage_start_s
    df["mode_s2"] = df["gps_available"].map({True: "GPS+IMU", False: "IMU-only"})

    df["x_s2"] = df["x_fused"]
    df["y_s2"] = df["y_fused"]

    mask_outage = ~df["gps_available"]
    df.loc[mask_outage, "x_s2"] = df.loc[mask_outage, "x_imu"]
    df.loc[mask_outage, "y_s2"] = df.loc[mask_outage, "y_imu"]

    df["t_outage"] = (df["time_s"] - outage_start_s).clip(lower=0.0)

    return df