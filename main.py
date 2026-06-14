from gps_imu_nav.pipeline import FusionPipeline
from gps_imu_nav.navigation import run_navigation


# =========================================================
#                DESCRIPTION DU PROJET
# =========================================================
"""
Fusion GPS + IMU

Objectif :
    Ce projet vise à traiter et fusionner des données issues de capteurs GPS et IMU.
    Le pipeline permet de nettoyer, synchroniser et structurer les données pour analyse.

Démarche générale :
    1. Chargement des données GPS et IMU
    2. Vérification et validation des fichiers
    3. Prétraitement des signaux
    4. Synchronisation temporelle GPS / IMU
    5. Construction d'un dataset final exploitable
    6. Calcul des trajectoires GPS, IMU et fusionnées
    7. Export des données en formats CSV et Pickle
"""


def main() -> None:
    pipeline = FusionPipeline()
    pipeline.run()

    navigation_results = run_navigation(alpha=0.7, save_output=True)

    print("\n====================================")
    print("TRAJECTOIRES ESTIMÉES")
    print("====================================\n")
    print(navigation_results.head(10))


if __name__ == "__main__":
    main()