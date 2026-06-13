"""
Module : chargeur_donnees.py
Description : Chargement robuste et validation des fichiers Excel GPS et IMU.
Projet de Session - MGA802
"""

from pathlib import Path
import pandas as pd


def charger_donnees_brutes(chemin_gps: str, chemin_imu: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Charger et valider les données GPS et IMU.
    1- Charger le fichier Excel
    2- Vérifier les colonnes GPS/IMU nécessaires
    """

    chemin_gps = Path(chemin_gps)
    chemin_imu = Path(chemin_imu)

    # Vérification de l'existence des fichiers
    if not chemin_gps.exists():
        raise FileNotFoundError(
            f"Le fichier GPS est introuvable :\n{chemin_gps.resolve()}"
        )

    if not chemin_imu.exists():
        raise FileNotFoundError(
            f"Le fichier IMU est introuvable :\n{chemin_imu.resolve()}"
        )

    print("Chargement des fichiers Excel...")

    # Lecture des fichiers Excel
    df_gps = pd.read_excel(chemin_gps)
    df_imu = pd.read_excel(chemin_imu)

    # Nettoyage des noms de colonnes
    df_gps.columns = df_gps.columns.str.strip()
    df_imu.columns = df_imu.columns.str.strip()

    print("\nColonnes GPS trouvées :")
    print(list(df_gps.columns))

    print("\nColonnes IMU trouvées :")
    print(list(df_imu.columns))

    # Colonnes attendues
    colonnes_gps_requises = [
        "Timestamp",
        "Latitude",
        "Longitude",
        "Altitude",
        "Vitesse Nord",
        "Vitesse Est",
    ]

    colonnes_imu_requises = [
        "Timestamp",
        "Yaw",
        "Pitch",
        "Roll",
        "Accel_X",
        "Accel_Y",
        "Accel_Z",
    ]

    # Validation GPS
    for col in colonnes_gps_requises:
        if col not in df_gps.columns:
            raise KeyError(
                f"Colonne GPS manquante : '{col}'\n"
                f"Colonnes disponibles : {list(df_gps.columns)}"
            )

    # Validation IMU
    for col in colonnes_imu_requises:
        if col not in df_imu.columns:
            raise KeyError(
                f"Colonne IMU manquante : '{col}'\n"
                f"Colonnes disponibles : {list(df_imu.columns)}"
            )

    print("\nValidation des colonnes réussie.")

    return (
        df_gps[colonnes_gps_requises],
        df_imu[colonnes_imu_requises],
    )


# ============================================================================
# TEST LOCAL
# ============================================================================

if __name__ == "__main__":

    print("Répertoire courant :", Path.cwd())

    # Projet-de-session_MGA-802_Groupe_A
    racine_projet = Path(__file__).resolve().parent.parent

    test_gps = racine_projet / "données" / "gps_locatisation.xlsx"
    test_imu = racine_projet / "données" / "IMUAcquisition.xlsx"

    print("\nChemin GPS :", test_gps)
    print("Chemin IMU :", test_imu)

    try:
        df_gps_brut, df_imu_brut = charger_donnees_brutes(
            test_gps,
            test_imu
        )

        print("\n=== CHARGEMENT RÉUSSI ===")
        print(f"Lignes GPS : {len(df_gps_brut)}")
        print(f"Lignes IMU : {len(df_imu_brut)}")

        print("\nAperçu GPS :")
        print(df_gps_brut.head())

        print("\nAperçu IMU :")
        print(df_imu_brut.head())

    except Exception as e:
        print(f"\n[ERREUR] {e}")