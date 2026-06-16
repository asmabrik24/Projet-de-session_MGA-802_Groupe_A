import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


DEFAULT_FIGURES_DIR_NAME = "figures"


class Graphique:
    """
    Génère les graphiques de validation.
    """

    def __init__(self):
        self.figures_dir = self.get_figures_dir()

    def get_project_root(self) -> Path:
        return Path(__file__).resolve().parent.parent

    def get_figures_dir(self) -> Path:
        figures_dir = self.get_project_root() / DEFAULT_FIGURES_DIR_NAME
        figures_dir.mkdir(parents=True, exist_ok=True)
        return figures_dir

    def _safe_show_or_close(self, show_plot: bool) -> None:
        if not show_plot:
            plt.close()
            return

        try:
            plt.show()
        except Exception as exc:
            print(f"[WARN] Affichage impossible : {exc}")
            plt.close()

    def plot_gps_outage(
        self,
        navigation_results: pd.DataFrame,
        save_figure: bool = True,
        output_path: str | os.PathLike | None = None,
        show_plot: bool = True,
    ) -> Path | None:

        required = ["time_s", "x_gps"]
        missing = [
            col for col in required
            if col not in navigation_results.columns
        ]

        if missing:
            raise ValueError(f"Colonnes manquantes : {missing}")

        plt.figure(figsize=(10, 6))
        plt.figure(figsize=(10, 6))

        plt.plot(
            navigation_results["time_s"],
            navigation_results["error_imu"],
            label="Erreur IMU",
            linewidth=2
        )

        plt.plot(
            navigation_results["time_s"],
            navigation_results["error_fused"],
            label="Erreur Fusion GPS/IMU",
            linewidth=2
        )

        plt.yscale("log")  # très important

        plt.xlabel("Temps [s]")
        plt.ylabel("Erreur de position [m]")
        plt.title("Évolution des erreurs de position")
        plt.legend()
        plt.grid(True, which="both")
        plt.tight_layout()

        plt.xlabel("Temps [s]")
        plt.ylabel("Erreur de position [m]")
        plt.title("Évolution des erreurs de position")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()


        plt.axvspan(
            1000,
            1300,
            alpha=0.3,
            label="Panne GPS")



        final_output_path = None

        if save_figure:
            final_output_path = (
                Path(output_path)
                if output_path is not None
                else self.figures_dir / "panne_gps.png"
            )
            plt.savefig(final_output_path, dpi=300, bbox_inches="tight")

        self._safe_show_or_close(show_plot)

        return final_output_path

    def plot_position_errors(
        self,
        navigation_results: pd.DataFrame,
        save_figure: bool = True,
        output_path: str | os.PathLike | None = None,
        show_plot: bool = True,
    ) -> Path | None:

        required = ["time_s", "error_imu", "error_fused"]
        missing = [
            col for col in required
            if col not in navigation_results.columns
        ]

        if missing:
            raise ValueError(f"Colonnes manquantes : {missing}")

        plt.figure(figsize=(10, 6))

        plt.plot(
            navigation_results["time_s"],
            navigation_results["error_imu"],
            label="Erreur IMU",
            linewidth=2
        )

        plt.plot(
            navigation_results["time_s"],
            navigation_results["error_fused"],
            label="Erreur Fusion GPS/IMU",
            linewidth=2
        )

        plt.xlabel("Temps [s]")
        plt.ylabel("Erreur de position [m]")
        plt.title("Évolution des erreurs de position")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        final_output_path = None

        if save_figure:
            final_output_path = (
                Path(output_path)
                if output_path is not None
                else self.figures_dir / "erreurs_position.png"
            )
            plt.savefig(final_output_path, dpi=300, bbox_inches="tight")

        self._safe_show_or_close(show_plot)

        return final_output_path

    def plot_rmse_comparison(
        self,
        rmse_results: dict,
        save_figure: bool = True,
        output_path: str | os.PathLike | None = None,
        show_plot: bool = True,
    ) -> Path | None:

        if not rmse_results:
            raise ValueError("Aucun résultat RMSE disponible.")

        labels = []
        values = []

        for method, result in rmse_results.items():
            labels.append(method.upper())
            values.append(result["rmse"])

        plt.figure(figsize=(8, 6))
        plt.bar(labels, values)

        # Affichage des valeurs numériques
        for i, v in enumerate(values):
            plt.text(
                i,
                v,
                f"{v:.2f}",
                ha="center",
                va="bottom"
            )

        # Échelle logarithmique
        plt.yscale("log")

        plt.xlabel("Méthode")
        plt.ylabel("RMSE [m]")
        plt.title("Comparaison des RMSE")
        plt.grid(axis="y")
        plt.tight_layout()

        final_output_path = None

        if save_figure:
            final_output_path = (
                Path(output_path)
                if output_path is not None
                else self.figures_dir / "comparaison_rmse.png"
            )
            plt.savefig(final_output_path, dpi=300, bbox_inches="tight")

        self._safe_show_or_close(show_plot)

        return final_output_path
