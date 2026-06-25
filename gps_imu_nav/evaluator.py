import numpy as np
import pandas as pd


class Evaluator:
    """
    Classe permettant d'évaluer les performances des méthodes
    de navigation IMU et Fusion GPS/IMU.

    Le GPS est utilisé comme trajectoire de référence pour le
    calcul des erreurs de position et du RMSE.
    """

    def calculate_position_error(
        self,
        x_reference,
        y_reference,
        x_estimated,
        y_estimated
    ):
        """
        Calcule l'erreur de position entre une trajectoire de
        référence et une trajectoire estimée.

        Parameters
        ----------
        x_reference, y_reference : array-like
            Coordonnées de référence (GPS).

        x_estimated, y_estimated : array-like
            Coordonnées estimées (IMU ou Fusion).

        Returns
        -------
        numpy.ndarray
            Erreur euclidienne pour chaque échantillon.
        """

        return np.sqrt(
            (x_estimated - x_reference) ** 2
            +
            (y_estimated - y_reference) ** 2
        )

    def calculate_rmse(self, errors):
        """
        Calcule la racine de l'erreur quadratique moyenne (RMSE).

        Parameters
        ----------
        errors : array-like
            Liste ou tableau des erreurs de position.

        Returns
        -------
        float
            Valeur du RMSE.

        Raises
        ------
        ValueError
            Si aucune erreur n'est fournie.
        """

        errors = np.array(errors)

        if len(errors) == 0:
            raise ValueError("Aucune erreur disponible.")

        return np.sqrt(np.nanmean(errors ** 2))

    def evaluate_all_available(self, data: pd.DataFrame):
        """
        Évalue les performances des trajectoires IMU et Fusion.

        Cette méthode :
        - vérifie la présence des colonnes requises ;
        - calcule les erreurs de position ;
        - calcule le RMSE de chaque méthode ;
        - retourne les résultats détaillés.

        Parameters
        ----------
        data : pandas.DataFrame
            Données contenant les coordonnées GPS,
            IMU et Fusion.

        Returns
        -------
        tuple
            results : DataFrame contenant les erreurs calculées.
            rmse_results : dictionnaire contenant les RMSE.

        Raises
        ------
        ValueError
            Si certaines colonnes requises sont absentes.
        """

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

        # Calcul des erreurs de position de la navigation IMU
        results["error_imu"] = self.calculate_position_error(
            results["x_gps"],
            results["y_gps"],
            results["x_imu"],
            results["y_imu"]
        )

        # Calcul des erreurs de position de la navigation Fusion
        results["error_fused"] = self.calculate_position_error(
            results["x_gps"],
            results["y_gps"],
            results["x_fused"],
            results["y_fused"]
        )

        # Calcul des RMSE pour chaque méthode
        rmse_results = {
            "imu": {
                "rmse": self.calculate_rmse(results["error_imu"])
            },
            "fusion": {
                "rmse": self.calculate_rmse(results["error_fused"])
            }
        }

        return results, rmse_results