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

import pandas as pd


def apply_time_window(df: pd.DataFrame, t_start: float, t_end: float | None) -> pd.DataFrame:
    """Filtre les résultats de navigation selon la fenêtre temporelle demandée."""
    if df.empty:
        raise ValueError("Les résultats de navigation sont vides avant l'application de la fenêtre temporelle.")

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
            f"La fenêtre temporelle choisie ne contient aucune donnée. Intervalle disponible : [{time_min:.3f}, {time_max:.3f}] s."
        )

    # Rebase le temps pour que la fenêtre sélectionnée démarre à 0 s.
    filtered = filtered.copy()
    filtered["time_s"] = filtered["time_s"] - float(filtered["time_s"].iloc[0])

    return filtered


def apply_navigation_mode(df: pd.DataFrame, nav_mode: str) -> pd.DataFrame:
    """Conserve uniquement les colonnes pertinentes selon le mode choisi."""
    out = df.copy()

    if nav_mode == "GPS_ONLY":
        cols_to_drop = [
            "x_imu", "y_imu", "vx_imu", "vy_imu",
            "x_fused", "y_fused", "vx_fused", "vy_fused",
        ]
    elif nav_mode == "IMU_ONLY":
        cols_to_drop = [
            "x_gps", "y_gps", "z_gps", "vx_gps", "vy_gps",
            "x_fused", "y_fused", "vx_fused", "vy_fused",
        ]
    else:
        cols_to_drop = []

    cols_to_drop = [col for col in cols_to_drop if col in out.columns]
    if cols_to_drop:
        out = out.drop(columns=cols_to_drop)

    return out

def main() -> None:
    """Point d'entree principal du projet MGA802."""
    pipeline = FusionPipeline()
    pipeline.run()

    preview_results = run_navigation(alpha=0.7, save_output=False)
    if preview_results.empty:
        raise ValueError("Aucun résultat de navigation n'a été généré pour la prévisualisation.")

    total_duration_s = None
    if "time_s" in preview_results.columns:
        preview_results = preview_results.copy()
        preview_results["time_s"] = pd.to_numeric(preview_results["time_s"], errors="coerce")
        preview_results = preview_results.dropna(subset=["time_s"])
        if not preview_results.empty:
            total_duration_s = float(preview_results["time_s"].max())

    ui = UserInterface()
    config = ui.get_user_config(total_duration_s=total_duration_s)

    alpha_value = config["alpha"] if config["alpha"] is not None else 0.7
    navigation_results = run_navigation(alpha=alpha_value, save_output=True)
    if navigation_results.empty:
        raise ValueError("Aucun résultat de navigation n'a été généré.")
    navigation_results = apply_time_window(
        navigation_results,
        t_start=config["t_start"],
        t_end=config["t_end"],
    )
    navigation_results = apply_navigation_mode(
        navigation_results,
        nav_mode=config["nav_mode"],
    )

    if config["show_plot"] and config["show_trajectory"] and {"x_gps", "y_gps"}.issubset(navigation_results.columns):
        plot_gps_trajectory_only(
            navigation_results,
            save_figure=True,
            show_plot=True,
        )

    print("\n====================================")
    print("TRAJECTOIRES ESTIMÉES")
    print("====================================\n")
    print(navigation_results.head(10))

    if config["show_plot"] and config["show_trajectory"]:
        if config["nav_mode"] == "FUSION":
            required_traj_cols = {
                "x_gps", "y_gps", "x_imu", "y_imu", "x_fused", "y_fused"
            }
            if required_traj_cols.issubset(set(navigation_results.columns)):
                plot_trajectories(
                    navigation_results,
                    save_figure=True,
                    show_plot=True,
                )
        elif config["nav_mode"] == "GPS_ONLY":
            print("[INFO] Le tracé comparatif complet est ignoré en mode GPS_ONLY.")
        elif config["nav_mode"] == "IMU_ONLY":
            print("[INFO] Le tracé comparatif complet est ignoré en mode IMU_ONLY.")

    if config["show_plot"] and config["show_velocities"]:
        required_vel_cols = {"vx_imu", "vy_imu", "vx_fused", "vy_fused"}
        if config["nav_mode"] == "FUSION" and required_vel_cols.issubset(set(navigation_results.columns)):
            plot_velocities(
                navigation_results,
                save_figure=True,
                show_plot=True,
            )
        else:
            print("[INFO] Le tracé des vitesses comparées est disponible uniquement en mode FUSION.")

    if {"x_gps", "y_gps", "x_imu", "y_imu", "x_fused", "y_fused"}.intersection(set(navigation_results.columns)):
        summary = summarize_navigation_results(navigation_results)
        print("\n====================================")
        print("RÉSUMÉ NAVIGATION")
        print("====================================\n")
        print(summary)

    if config["nav_mode"] == "FUSION":
        scenario2_df = simulate_gps_outage(
            navigation_results,
            outage_start_s=config["outage_start"],
        )
        scenario2_df = compute_position_errors(
            scenario2_df,
            x_est_col="x_s2",
            y_est_col="y_s2",
            x_ref_col="x_gps",
            y_ref_col="y_gps",
            prefix="s2_err",
        )

        scenario2_gps_phase = scenario2_df[scenario2_df["gps_available"]].copy()

        print("\n====================================")
        print("SCÉNARIO 2 — STATISTIQUES")
        print("====================================\n")

        if scenario2_gps_phase.empty:
            print("[INFO] Aucune phase GPS disponible dans le scénario 2 avec la configuration actuelle.")
        else:
            s2_stats = summarize_error_statistics(
                scenario2_gps_phase,
                err_2d_col="s2_err_2d",
            )
            print(s2_stats)

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
        print("\n[INFO] Le scénario de panne GPS est ignoré car il nécessite le mode FUSION.")


if __name__ == "__main__":
    main()