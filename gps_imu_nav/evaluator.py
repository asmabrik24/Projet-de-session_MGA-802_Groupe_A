import numpy as np
import pandas as pd


class Evaluator:
    """
    Calcule les erreurs de position et le RMSE.
    Le GPS est utilisé comme référence.
    """

    def calculate_position_error(
        self,
        x_reference,
        y_reference,
        x_estimated,
        y_estimated
    ):
        return np.sqrt(
            (x_estimated - x_reference) ** 2
            +
            (y_estimated - y_reference) ** 2
        )

    def calculate_rmse(self, errors):
        errors = np.array(errors)

        if len(errors) == 0:
            raise ValueError("Aucune erreur disponible.")

        return np.sqrt(np.nanmean(errors ** 2))

    def evaluate_all_available(self, data: pd.DataFrame):
        results = data.copy()

        required_columns = [
            "x_gps",
            "y_gps",
            "x_imu",
            "y_imu",
            "x_fused",
            "y_fused"
        ]

        missing_columns = [
            col for col in required_columns
            if col not in results.columns
        ]

        if missing_columns:
            raise ValueError(f"Colonnes manquantes : {missing_columns}")

        results["error_imu"] = self.calculate_position_error(
            results["x_gps"],
            results["y_gps"],
            results["x_imu"],
            results["y_imu"]
        )

        results["error_fused"] = self.calculate_position_error(
            results["x_gps"],
            results["y_gps"],
            results["x_fused"],
            results["y_fused"]
        )

        rmse_results = {
            "imu": {
                "rmse": self.calculate_rmse(results["error_imu"])
            },
            "fusion": {
                "rmse": self.calculate_rmse(results["error_fused"])
            }
        }

        return results, rmse_results