import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DEFAULT_FIGURES_DIR_NAME = "figures"


def _safe_show_or_close(show_plot: bool) -> None:
    """
    Tente d'afficher la figure. Si le backend matplotlib de PyCharm échoue,
    on ferme proprement la figure sans interrompre l'exécution.
    """
    if not show_plot:
        plt.close()
        return

    try:
        plt.show()
    except Exception as exc:
        print(f"[WARN] Affichage matplotlib impossible dans cet environnement : {exc}")
        plt.close()


def get_project_root() -> Path:
    """Retourne la racine du projet à partir du dossier du module."""
    return Path(__file__).resolve().parent.parent


def get_figures_dir() -> Path:
    """Retourne le dossier de sortie des figures."""
    figures_dir = get_project_root() / DEFAULT_FIGURES_DIR_NAME
    figures_dir.mkdir(parents=True, exist_ok=True)
    return figures_dir


def validate_navigation_results(navigation_results: pd.DataFrame) -> None:
    """Vérifie que les colonnes minimales nécessaires aux graphiques existent."""
    required = ["x_gps", "y_gps", "x_imu", "y_imu", "x_fused", "y_fused"]
    missing = [col for col in required if col not in navigation_results.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes pour la visualisation : {missing}")


def plot_trajectories(
    navigation_results: pd.DataFrame,
    save_figure: bool = True,
    output_path: str | os.PathLike | None = None,
    show_plot: bool = True,
) -> Path | None:
    """
    Affiche d'abord une vue utile GPS + fusion, puis une vue complète
    incluant la dérive IMU.
    """
    validate_navigation_results(navigation_results)

    # --------------------------------------------------
    # Figure 1 : vue utile GPS + fusion
    # --------------------------------------------------
    plt.figure(figsize=(10, 6))
    plt.plot(
        navigation_results["x_gps"],
        navigation_results["y_gps"],
        label="GPS seul",
        linewidth=2,
    )
    plt.plot(
        navigation_results["x_fused"],
        navigation_results["y_fused"],
        label="Fusion GPS/IMU",
        linewidth=2,
    )

    plt.scatter(
        navigation_results["x_gps"].iloc[0],
        navigation_results["y_gps"].iloc[0],
        marker="s",
        s=60,
        label="Départ GPS",
    )
    plt.scatter(
        navigation_results["x_gps"].iloc[-1],
        navigation_results["y_gps"].iloc[-1],
        marker="X",
        s=70,
        label="Arrivée GPS",
    )

    x_focus = pd.concat([
        navigation_results["x_gps"],
        navigation_results["x_fused"],
    ]).astype(float)
    y_focus = pd.concat([
        navigation_results["y_gps"],
        navigation_results["y_fused"],
    ]).astype(float)

    x_min, x_max = x_focus.min(), x_focus.max()
    y_min, y_max = y_focus.min(), y_focus.max()

    x_margin = max(50.0, 0.1 * max(1.0, x_max - x_min))
    y_margin = max(50.0, 0.1 * max(1.0, y_max - y_min))

    plt.xlim(x_min - x_margin, x_max + x_margin)
    plt.ylim(y_min - y_margin, y_max + y_margin)

    plt.axis("equal")
    plt.xlabel("Position x [m]")
    plt.ylabel("Position y [m]")
    plt.title("Trajectoire utile : GPS et fusion")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    focused_output_path = None
    if save_figure:
        focused_output_path = Path(output_path) if output_path is not None else get_figures_dir() / "trajectoires_gps_fusion.png"
        plt.savefig(focused_output_path, dpi=300, bbox_inches="tight")

    _safe_show_or_close(show_plot)

    # --------------------------------------------------
    # Figure 2 : vue complète avec dérive IMU
    # --------------------------------------------------
    plt.figure(figsize=(10, 6))
    plt.plot(
        navigation_results["x_gps"],
        navigation_results["y_gps"],
        label="GPS seul",
        linewidth=2,
    )
    plt.plot(
        navigation_results["x_fused"],
        navigation_results["y_fused"],
        label="Fusion GPS/IMU",
        linewidth=2,
    )
    plt.plot(
        navigation_results["x_imu"],
        navigation_results["y_imu"],
        label="IMU seule",
        linewidth=1,
        linestyle="--",
        alpha=0.6,
    )

    plt.xlabel("Position x [m]")
    plt.ylabel("Position y [m]")
    plt.title("Comparaison complète avec dérive IMU")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    if save_figure:
        full_output_path = get_figures_dir() / "trajectoires_completes.png"
        plt.savefig(full_output_path, dpi=300, bbox_inches="tight")

    _safe_show_or_close(show_plot)

    return focused_output_path


def plot_gps_trajectory_only(
    navigation_results: pd.DataFrame,
    save_figure: bool = True,
    output_path: str | os.PathLike | None = None,
    show_plot: bool = True,
) -> Path | None:
    """
    Trace uniquement la trajectoire GPS pour retrouver clairement la forme
    de référence sans être écrasée par la dérive IMU.
    """
    required = ["x_gps", "y_gps"]
    missing = [col for col in required if col not in navigation_results.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes pour la trajectoire GPS : {missing}")

    plt.figure(figsize=(8, 6))
    plt.plot(
        navigation_results["x_gps"],
        navigation_results["y_gps"],
        linewidth=2,
        label="GPS seul",
    )
    plt.scatter(
        navigation_results["x_gps"].iloc[0],
        navigation_results["y_gps"].iloc[0],
        marker="s",
        s=60,
        label="Départ",
    )
    plt.scatter(
        navigation_results["x_gps"].iloc[-1],
        navigation_results["y_gps"].iloc[-1],
        marker="X",
        s=70,
        label="Arrivée",
    )

    plt.xlabel("Position x [m]")
    plt.ylabel("Position y [m]")
    plt.title("Trajectoire GPS seule")
    plt.legend()
    plt.grid(True)
    plt.axis("equal")
    plt.tight_layout()

    final_output_path = None
    if save_figure:
        final_output_path = Path(output_path) if output_path is not None else get_figures_dir() / "trajectoire_gps_seule.png"
        plt.savefig(final_output_path, dpi=300, bbox_inches="tight")

    _safe_show_or_close(show_plot)

    return final_output_path


def plot_velocities(
    navigation_results: pd.DataFrame,
    save_figure: bool = True,
    output_path: str | os.PathLike | None = None,
    show_plot: bool = True,
) -> Path | None:
    """
    Trace les vitesses IMU et fusionnées si elles sont disponibles.
    """
    required = ["time_s", "vx_imu", "vy_imu"]
    missing = [col for col in required if col not in navigation_results.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes pour les vitesses : {missing}")

    plt.figure(figsize=(10, 6))
    plt.plot(navigation_results["time_s"], navigation_results["vx_imu"], label="vx IMU", linewidth=2)
    plt.plot(navigation_results["time_s"], navigation_results["vy_imu"], label="vy IMU", linewidth=2)

    if "vx_fused" in navigation_results.columns:
        plt.plot(navigation_results["time_s"], navigation_results["vx_fused"], label="vx fusion", linestyle="--")
    if "vy_fused" in navigation_results.columns:
        plt.plot(navigation_results["time_s"], navigation_results["vy_fused"], label="vy fusion", linestyle="--")

    plt.xlabel("Temps [s]")
    plt.ylabel("Vitesse [m/s]")
    plt.title("Évolution des vitesses estimées")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    final_output_path = None
    if save_figure:
        final_output_path = Path(output_path) if output_path is not None else get_figures_dir() / "vitesses_comparees.png"
        plt.savefig(final_output_path, dpi=300, bbox_inches="tight")

    _safe_show_or_close(show_plot)

    return final_output_path


def summarize_navigation_results(navigation_results: pd.DataFrame) -> pd.DataFrame:
    """
    Retourne un petit tableau résumé des positions finales.
    """
    validate_navigation_results(navigation_results)

    summary = pd.DataFrame({
        "mode": ["GPS", "IMU", "Fusion"],
        "x_final_m": [
            float(navigation_results["x_gps"].iloc[-1]),
            float(navigation_results["x_imu"].iloc[-1]),
            float(navigation_results["x_fused"].iloc[-1]),
        ],
        "y_final_m": [
            float(navigation_results["y_gps"].iloc[-1]),
            float(navigation_results["y_imu"].iloc[-1]),
            float(navigation_results["y_fused"].iloc[-1]),
        ],
    })

    return summary

def plot_scenario2_trajectory(
    scenario2_df: pd.DataFrame,
    outage_start_s: float = 30.0,
    save_figure: bool = True,
    output_path: str | os.PathLike | None = None,
    show_plot: bool = True,
) -> Path | None:
    required = ["x_gps", "y_gps", "x_s2", "y_s2", "gps_available", "time_s"]
    missing = [col for col in required if col not in scenario2_df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes pour la figure scénario 2 : {missing}")

    df = scenario2_df.copy()

    plt.figure(figsize=(10, 6))

    plt.plot(
        df["x_gps"],
        df["y_gps"],
        label="GPS référence",
        linewidth=2,
        linestyle="--",
        marker="o",
        markersize=2,
    )

    mask_fusion = df["gps_available"]
    mask_imu = ~df["gps_available"]

    plt.plot(
        df.loc[mask_fusion, "x_s2"],
        df.loc[mask_fusion, "y_s2"],
        label="GPS+IMU Fusion (0–30 s)",
        linewidth=2,
    )

    plt.plot(
        df.loc[mask_imu, "x_s2"],
        df.loc[mask_imu, "y_s2"],
        label="IMU-only Dead Reckoning (> 30 s)",
        linewidth=2,
    )

    idx_outage = (df["time_s"] - outage_start_s).abs().idxmin()

    plt.scatter(df["x_gps"].iloc[0], df["y_gps"].iloc[0], marker="s", s=60, label="Start")
    plt.scatter(df["x_s2"].iloc[-1], df["y_s2"].iloc[-1], marker="^", s=70, label="End")
    plt.scatter(
        df.loc[idx_outage, "x_gps"],
        df.loc[idx_outage, "y_gps"],
        marker="v",
        s=70,
        label="GPS Outage Point",
    )

    plt.xlabel("East (m)")
    plt.ylabel("North (m)")
    plt.title("Scenario 2 — 2D Trajectory: GPS Outage after 30 s")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    final_output_path = None
    if save_figure:
        final_output_path = (
            Path(output_path)
            if output_path is not None
            else get_figures_dir() / "S2_trajectory_outage.png"
        )
        plt.savefig(final_output_path, dpi=300, bbox_inches="tight")

    _safe_show_or_close(show_plot)
    return final_output_path


def plot_scenario2_drift(
    scenario2_df: pd.DataFrame,
    save_figure: bool = True,
    output_path: str | os.PathLike | None = None,
    show_plot: bool = True,
) -> Path | None:
    required = ["time_s", "t_outage", "gps_available", "s2_err_2d", "s2_err_x", "s2_err_y"]
    missing = [col for col in required if col not in scenario2_df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes pour la dérive scénario 2 : {missing}")

    df = scenario2_df.copy()

    fig, axes = plt.subplots(2, 1, figsize=(10, 8))

    mask_fusion = df["gps_available"]
    mask_imu = ~df["gps_available"]

    axes[0].plot(df.loc[mask_fusion, "time_s"], df.loc[mask_fusion, "s2_err_2d"], label="GPS+IMU phase")
    axes[0].plot(df.loc[mask_imu, "time_s"], df.loc[mask_imu, "s2_err_2d"], label="IMU-only phase")
    axes[0].axvline(30.0, linestyle="--", color="black", label="GPS Outage")
    axes[0].set_title("Position Error vs. GPS Reference — Full Window")
    axes[0].set_ylabel("2D Horizontal Error (m)")
    axes[0].grid(True)
    axes[0].legend()

    axes[1].plot(df.loc[mask_imu, "t_outage"], df.loc[mask_imu, "s2_err_x"], label="North")
    axes[1].plot(df.loc[mask_imu, "t_outage"], df.loc[mask_imu, "s2_err_y"], label="East")
    if "s2_err_z" in df.columns:
        axes[1].plot(df.loc[mask_imu, "t_outage"], df.loc[mask_imu, "s2_err_z"], label="Down")
    axes[1].set_title("NED Error Components after GPS Outage")
    axes[1].set_xlabel("Time since GPS outage (s)")
    axes[1].set_ylabel("Position Error (m)")
    axes[1].grid(True)
    axes[1].legend()

    plt.tight_layout()

    final_output_path = None
    if save_figure:
        final_output_path = (
            Path(output_path)
            if output_path is not None
            else get_figures_dir() / "S2_drift_analysis.png"
        )
        plt.savefig(final_output_path, dpi=300, bbox_inches="tight")

    _safe_show_or_close(show_plot)
    return final_output_path


def plot_scenario2_navigation_states(
    scenario2_df: pd.DataFrame,
    outage_start_s: float = 30.0,
    save_figure: bool = True,
    output_path: str | os.PathLike | None = None,
    show_plot: bool = True,
) -> Path | None:
    required = ["time_s"]
    missing = [col for col in required if col not in scenario2_df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes pour les états scénario 2 : {missing}")

    df = scenario2_df.copy()
    df = df.sort_values("time_s").reset_index(drop=True)

    if "vx_imu" in df.columns and "vy_imu" in df.columns:
        df["horizontal_speed"] = (df["vx_imu"] ** 2 + df["vy_imu"] ** 2) ** 0.5
    else:
        raise ValueError("Colonnes vx_imu et vy_imu requises pour la vitesse horizontale.")

    if "yaw" in df.columns:
        df["heading_plot"] = df["yaw"]
    else:
        if "x_s2" not in df.columns or "y_s2" not in df.columns:
            raise ValueError(
                "Colonnes manquantes pour les états scénario 2 : ['yaw'] et aucune trajectoire x_s2/y_s2 disponible pour approximer le cap."
            )

        dx = df["x_s2"].diff().fillna(0.0)
        dy = df["y_s2"].diff().fillna(0.0)
        df["heading_plot"] = np.degrees(np.arctan2(dy, dx))
        df["heading_plot"] = (
            df["heading_plot"]
            .replace([np.inf, -np.inf], np.nan)
            .ffill()
            .bfill()
            .fillna(0.0)
        )

    fig, axes = plt.subplots(2, 1, figsize=(10, 8))

    axes[0].plot(df["time_s"], df["horizontal_speed"])
    axes[0].axvline(outage_start_s, linestyle="--", color="black", label="GPS Outage")
    axes[0].set_title("Horizontal Speed Estimate")
    axes[0].set_ylabel("Horizontal Speed (m/s)")
    axes[0].grid(True)
    axes[0].legend()

    axes[1].plot(df["time_s"], df["heading_plot"])
    axes[1].axvline(outage_start_s, linestyle="--", color="black", label="GPS Outage")
    axes[1].set_title("Heading (Yaw) Estimate")
    axes[1].set_xlabel("Time (s)")
    axes[1].set_ylabel("Yaw / Heading (deg)")
    axes[1].grid(True)
    axes[1].legend()

    plt.tight_layout()

    final_output_path = None
    if save_figure:
        final_output_path = (
            Path(output_path)
            if output_path is not None
            else get_figures_dir() / "S2_navigation_states.png"
        )
        plt.savefig(final_output_path, dpi=300, bbox_inches="tight")

    _safe_show_or_close(show_plot)
    return final_output_path