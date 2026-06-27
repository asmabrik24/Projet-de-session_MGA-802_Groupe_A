"""
main.py

Point d'entrée principal du projet de fusion GPS/IMU.

Ce script orchestre :
- l'exécution du pipeline de traitement des données ;
- la lecture et la validation des paramètres utilisateur ;
- le calcul des trajectoires GPS, IMU et fusionnées ;
- l'application d'une fenêtre temporelle d'analyse ;
- la simulation d'une panne GPS ;
- le calcul des erreurs de position ;
- la génération des graphiques et l'affichage des résultats.

Projet réalisé dans le cadre du cours MGA802.
"""

import pandas as pd

from gps_imu_nav.pipeline import FusionPipeline
from gps_imu_nav.navigation import run_navigation
from gps_imu_nav.visualization import plot_gps_trajectory_only
from gps_imu_nav.visualization import (
    plot_trajectories,
    plot_velocities,
    summarize_navigation_results,
    plot_scenario2_trajectory,
    plot_scenario2_drift,
    plot_scenario2_navigation_states,
)
from gps_imu_nav.scenario2 import simulate_gps_outage
from gps_imu_nav.metrics import compute_position_errors, summarize_error_statistics
from gps_imu_nav.user_interface import UserInterface


TRAJ_COLS = {"x_gps", "y_gps", "x_imu", "y_imu", "x_fused", "y_fused"}
VEL_COLS = {"vx_imu", "vy_imu", "vx_fused", "vy_fused"}


def apply_time_window(
    df: pd.DataFrame,
    t_start: float,
    t_end: float | None
) -> pd.DataFrame:
    """
    Filtre les résultats de navigation selon une fenêtre temporelle.

    :param df: Résultats de navigation.
    :type df: pandas.DataFrame
    :param t_start: Temps de début de la fenêtre en secondes.
    :type t_start: float
    :param t_end: Temps de fin de la fenêtre en secondes. Si None, la fin du fichier est utilisée.
    :type t_end: float | None
    :return: Résultats filtrés avec un temps recalé à 0 seconde.
    :rtype: pandas.DataFrame
    :raises ValueError: Si les données sont vides ou si la fenêtre choisie ne contient aucune donnée.
    """
    if df.empty:
        raise ValueError(
            "Les résultats de navigation sont vides avant l'application de la fenêtre temporelle."
        )

    if "time_s" not in df.columns:
        return df.copy()

    out = df.copy()
    out["time_s"] = pd.to_numeric(out["time_s"], errors="coerce")
    out = out.dropna(subset=["time_s"]).sort_values("time_s").reset_index(drop=True)

    if out.empty:
        raise ValueError("La colonne time_s ne contient aucune valeur exploitable.")

    time_min = float(out["time_s"].min())
    time_max = float(out["time_s"].max())

    if t_start < time_min:
        t_start = time_min

    if t_end is not None and t_end > time_max:
        t_end = time_max

    filtered = out[out["time_s"] >= t_start]

    if t_end is not None:
        filtered = filtered[filtered["time_s"] <= t_end]

    filtered = filtered.reset_index(drop=True)

    if filtered.empty:
        raise ValueError(
            f"La fenêtre temporelle choisie ne contient aucune donnée. "
            f"Intervalle disponible : [{time_min:.3f}, {time_max:.3f}] s."
        )

    # Recale le temps afin que la fenêtre sélectionnée démarre à 0 s.
    filtered = filtered.copy()
    filtered["time_s"] = filtered["time_s"] - float(filtered["time_s"].iloc[0])

    return filtered


def apply_navigation_mode(
    df: pd.DataFrame,
    nav_mode: str
) -> pd.DataFrame:
    """
    Conserve uniquement les colonnes pertinentes selon le mode de navigation choisi.

    :param df: Résultats de navigation.
    :type df: pandas.DataFrame
    :param nav_mode: Mode de navigation choisi par l'utilisateur.
    :type nav_mode: str
    :return: Résultats contenant seulement les colonnes utiles au mode choisi.
    :rtype: pandas.DataFrame
    """
    out = df.copy()

    cols_to_drop_by_mode = {
        "GPS_ONLY": [
            "x_imu", "y_imu", "vx_imu", "vy_imu",
            "x_fused", "y_fused", "vx_fused", "vy_fused",
        ],
        "IMU_ONLY": [
            "x_gps", "y_gps", "z_gps", "vx_gps", "vy_gps",
            "x_fused", "y_fused", "vx_fused", "vy_fused",
        ],
        "FUSION": [],
    }

    cols_to_drop = cols_to_drop_by_mode.get(nav_mode, [])

    cols_to_drop = [col for col in cols_to_drop if col in out.columns]

    if cols_to_drop:
        out = out.drop(columns=cols_to_drop)

    return out


def _print_section(title: str) -> None:
    """Affiche un titre de section homogène dans le terminal."""
    print("\n====================================")
    print(title)
    print("====================================\n")


def _has_any_columns(df: pd.DataFrame, columns: set[str]) -> bool:
    """Vérifie si au moins une colonne de l'ensemble est présente."""
    return any(col in df.columns for col in columns)


def main() -> None:
    """
    Fonction principale du projet.

    Elle coordonne les différentes étapes de l'exécution :
    initialisation du pipeline, lecture des paramètres utilisateur,
    navigation, simulation de panne GPS, évaluation des performances
    et visualisation des résultats.
    """
    # =====================================================
    # 1. Exécution du pipeline principal
    # =====================================================
    pipeline = FusionPipeline()
    pipeline.run()

    # =====================================================
    # 2. Prévisualisation pour déterminer la durée disponible
    # =====================================================
    preview_results = run_navigation(alpha=0.7, save_output=False)

    if preview_results.empty:
        raise ValueError(
            "Aucun résultat de navigation n'a été généré pour la prévisualisation."
        )

    total_duration_s = None

    if "time_s" in preview_results.columns:
        preview_results = preview_results.copy()
        preview_results["time_s"] = pd.to_numeric(
            preview_results["time_s"],
            errors="coerce"
        )
        preview_results = preview_results.dropna(subset=["time_s"])

        if not preview_results.empty:
            total_duration_s = float(preview_results["time_s"].max())

    # =====================================================
    # 3. Lecture et validation des paramètres utilisateur
    # =====================================================
    ui = UserInterface()
    config = ui.get_user_config(total_duration_s=total_duration_s)

    # =====================================================
    # 4. Exécution de la navigation selon les paramètres
    # =====================================================
    alpha_value = config["alpha"] if config["alpha"] is not None else 0.7

    navigation_results = run_navigation(
        alpha=alpha_value,
        save_output=True
    )

    if navigation_results.empty:
        raise ValueError("Aucun résultat de navigation n'a été généré.")

    # =====================================================
    # 5. Application de la fenêtre temporelle choisie
    # =====================================================
    navigation_results = apply_time_window(
        navigation_results,
        t_start=config["t_start"],
        t_end=config["t_end"],
    )

    # =====================================================
    # 6. Application du mode de navigation choisi
    # =====================================================
    navigation_results = apply_navigation_mode(
        navigation_results,
        nav_mode=config["nav_mode"],
    )

    # =====================================================
    # 7. Affichage de la trajectoire GPS seule
    # =====================================================
    if (
        config["show_plot"]
        and config["show_trajectory"]
        and {"x_gps", "y_gps"}.issubset(navigation_results.columns)
    ):
        plot_gps_trajectory_only(
            navigation_results,
            save_figure=True,
            show_plot=True,
        )

    # =====================================================
    # 8. Affichage des premières lignes des résultats
    # =====================================================
    _print_section("TRAJECTOIRES ESTIMÉES")
    print(navigation_results.head(10))

    # =====================================================
    # 9. Affichage des trajectoires comparatives
    # =====================================================
    if config["show_plot"] and config["show_trajectory"]:
        if config["nav_mode"] == "FUSION":
            if TRAJ_COLS.issubset(set(navigation_results.columns)):
                plot_trajectories(
                    navigation_results,
                    save_figure=True,
                    show_plot=True,
                )
        else:
            print(
                f"[INFO] Le tracé comparatif complet est ignoré en mode {config['nav_mode']}."
            )

    # =====================================================
    # 10. Affichage des vitesses estimées
    # =====================================================
    if config["show_plot"] and config["show_velocities"]:
        if config["nav_mode"] == "FUSION" and VEL_COLS.issubset(set(navigation_results.columns)):
            plot_velocities(
                navigation_results,
                save_figure=True,
                show_plot=True,
            )
        else:
            print(
                "[INFO] Le tracé des vitesses comparées est disponible uniquement en mode FUSION."
            )

    # =====================================================
    # 11. Résumé des résultats de navigation
    # =====================================================
    if _has_any_columns(navigation_results, TRAJ_COLS):
        summary = summarize_navigation_results(navigation_results)
        _print_section("RÉSUMÉ NAVIGATION")
        print(summary)

    # =====================================================
    # 12. Simulation du scénario de panne GPS
    # =====================================================
    if config["nav_mode"] == "FUSION":
        scenario2_df = simulate_gps_outage(
            navigation_results,
            outage_start_s=config["outage_start"],
        )

        # =================================================
        # 13. Calcul des erreurs de position du scénario 2
        # =================================================
        scenario2_df = compute_position_errors(
            scenario2_df,
            x_est_col="x_s2",
            y_est_col="y_s2",
            x_ref_col="x_gps",
            y_ref_col="y_gps",
            prefix="s2_err",
        )

        scenario2_gps_phase = scenario2_df[
            scenario2_df["gps_available"]
        ].copy()

        _print_section("SCÉNARIO 2 — STATISTIQUES")

        if scenario2_gps_phase.empty:
            print(
                "[INFO] Aucune phase GPS disponible dans le scénario 2 "
                "avec la configuration actuelle."
            )
        else:
            s2_stats = summarize_error_statistics(
                scenario2_gps_phase,
                err_2d_col="s2_err_2d",
            )
            print(s2_stats)

        # =================================================
        # 14. Génération des graphiques du scénario 2
        # =================================================
        if config["show_plot"] and config["show_trajectory"]:
            plot_scenario2_trajectory(
                scenario2_df,
                outage_start_s=config["outage_start"],
                save_figure=True,
                show_plot=True,
            )

            plot_scenario2_drift(
                scenario2_df,
                save_figure=True,
                show_plot=True,
            )

            plot_scenario2_navigation_states(
                scenario2_df,
                outage_start_s=config["outage_start"],
                save_figure=True,
                show_plot=True,
            )

    else:
        print(
            "\n[INFO] Le scénario de panne GPS est ignoré "
            "car il nécessite le mode FUSION."
        )


if __name__ == "__main__":
    main()