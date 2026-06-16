from gps_imu_nav.pipeline import FusionPipeline
from gps_imu_nav.navigation import run_navigation
from gps_imu_nav.visualization import plot_gps_trajectory_only
from gps_imu_nav.visualization import (
    plot_trajectories,
    plot_velocities,
    summarize_navigation_results,
)
from gps_imu_nav.user_interface import UserInterface
from gps_imu_nav.gps_outage import GPSOutageSimulator
from gps_imu_nav.evaluator import Evaluator
from gps_imu_nav.graphique import Graphique

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
    """Point d'entree principal du projet MGA802."""
    ui = UserInterface()
    config = ui.get_user_config()


    pipeline = FusionPipeline()
    pipeline.run()

    navigation_results = run_navigation(alpha=0.7, save_output=True)
    plot_gps_trajectory_only(navigation_results, save_figure=True, show_plot=True)
    gps_outage = GPSOutageSimulator(navigation_results)

    navigation_results = gps_outage.simulate_outage(
        start_time=10,
        duration=5

    )

    evaluator = Evaluator()

    navigation_results, rmse_results = evaluator.evaluate_all_available(
        navigation_results
    )

    graphique = Graphique()

    graphique.plot_gps_outage(
        navigation_results,
        save_figure=True,
        show_plot=True
    )

    graphique.plot_position_errors(
        navigation_results,
        save_figure=True,
        show_plot=True
    )

    graphique.plot_rmse_comparison(
        rmse_results,
        save_figure=True,
        show_plot=True
    )

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

    # =====================================================
    # INTERACTION UTILISATEUR
    # =====================================================

    print("\n====================================")
    print("PARAMÈTRES UTILISATEUR")
    print("====================================\n")

    mode = input(
        "Mode de navigation (GPS / IMU / FUSION) : "
    ).upper()

    outage_duration = float(
        input("Durée de la panne GPS simulée (s) : ")
    )

    afficher_graphiques = input(
        "Afficher les graphiques ? (o/n) : "
    ).lower()

    afficher_resultats = input(
        "Afficher les résultats numériques ? (o/n) : "
    ).lower()

    print("\n====================================")
    print("CHOIX UTILISATEUR")
    print("====================================\n")

    print(f"Mode sélectionné : {mode}")
    print(f"Durée panne GPS : {outage_duration} s")
    print(f"Afficher graphiques : {afficher_graphiques}")
    print(f"Afficher résultats : {afficher_resultats}")


if __name__ == "__main__":
    main()