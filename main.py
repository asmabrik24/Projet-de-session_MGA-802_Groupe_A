from gps_imu_nav.pipeline import FusionPipeline
from gps_imu_nav.navigation import run_navigation
from gps_imu_nav.visualization import plot_gps_trajectory_only
from gps_imu_nav.visualization import (
    plot_trajectories,
    plot_velocities,
    summarize_navigation_results,
)


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
    7. Visualisation des trajectoires et des vitesses
    8. Export des données en formats CSV et Pickle
"""


def main() -> None:
    pipeline = FusionPipeline()
    pipeline.run()

    navigation_results = run_navigation(alpha=0.7, save_output=True)
    plot_gps_trajectory_only(navigation_results, save_figure=True, show_plot=True)
    print("\n====================================")
    print("TRAJECTOIRES ESTIMÉES")
    print("====================================\n")
    print(navigation_results.head(10))

    plot_trajectories(navigation_results, save_figure=True, show_plot=True)
    plot_velocities(navigation_results, save_figure=True, show_plot=True)

    summary = summarize_navigation_results(navigation_results)
    print("\n====================================")
    print("RÉSUMÉ NAVIGATION")
    print("====================================\n")
    print(summary)


if __name__ == "__main__":
    main()