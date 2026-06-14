from gps_imu_nav.pipeline import FusionPipeline


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
    6. Export des données en formats CSV et Pickle
"""


def main() -> None:
    pipeline = FusionPipeline()
    pipeline.run()


if __name__ == "__main__":
    main()