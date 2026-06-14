import os
from pathlib import Path

import matplotlib.pyplot as plt
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