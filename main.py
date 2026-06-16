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


def main() -> None:
    """Point d'entree principal du projet MGA802."""
    ui = UserInterface()
    config = ui.get_user_config()


    pipeline = FusionPipeline()
    pipeline.run()

    navigation_results = run_navigation(alpha=0.7, save_output=True)

    plot_gps_trajectory_only(
        navigation_results,
        save_figure=True,
        show_plot=True,
    )

    print("\n====================================")
    print("TRAJECTOIRES ESTIMÉES")
    print("====================================\n")
    print(navigation_results.head(10))

    plot_trajectories(
        navigation_results,
        save_figure=True,
        show_plot=True,
    )
    plot_velocities(
        navigation_results,
        save_figure=True,
        show_plot=True,
    )

    summary = summarize_navigation_results(navigation_results)
    print("\n====================================")
    print("RÉSUMÉ NAVIGATION")
    print("====================================\n")
    print(summary)

    scenario2_df = simulate_gps_outage(
        navigation_results,
        outage_start_s=30.0,
    )
    scenario2_df = compute_position_errors(
        scenario2_df,
        x_est_col="x_s2",
        y_est_col="y_s2",
        x_ref_col="x_gps",
        y_ref_col="y_gps",
        prefix="s2_err",
    )

    s2_stats = summarize_error_statistics(
        scenario2_df[scenario2_df["gps_available"]],
        err_2d_col="s2_err_2d",
    )

    print("\n====================================")
    print("SCÉNARIO 2 — STATISTIQUES")
    print("====================================\n")
    print(s2_stats)

    plot_scenario2_trajectory(
        scenario2_df,
        outage_start_s=30.0,
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
        outage_start_s=30.0,
        save_figure=True,
        show_plot=True,
    )


if __name__ == "__main__":
    main()