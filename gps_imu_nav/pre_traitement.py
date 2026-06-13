"""
Module : pre_traitement_donnees.py
Prétraitement GPS / IMU complet
"""

import pandas as pd


class Pretraitement:
    """
    Pipeline complet GPS / IMU :
    - vérification colonnes
    - nettoyage
    - conversion unités
    - synchronisation
    - export HDF5
    """

    # =========================================================
    # INITIALISATION
    # =========================================================

    def __init__(self, donnees: pd.DataFrame):
        self.donnees = donnees.copy()

    # =========================================================
    # 1. VERIFICATION COLONNES
    # =========================================================

    def verifier_colonnes(self):
        """
        Vérifie la présence des colonnes GPS et IMU.
        """

        colonnes_gps = ["timestamp", "latitude", "longitude"]
        colonnes_imu = ["ax", "ay", "az", "gx", "gy", "gz"]

        manquantes = []

        for col in colonnes_gps + colonnes_imu:
            if col not in self.donnees.columns:
                manquantes.append(col)

        if manquantes:
            raise ValueError(f"Colonnes manquantes : {manquantes}")

        return self.donnees

    # =========================================================
    # 2. NETTOYAGE
    # =========================================================

    def nettoyer(self):
        """
        Nettoyage des données.
        """

        self.donnees = self.donnees.drop_duplicates()

        # valeurs manquantes
        self.donnees = self.donnees.interpolate(method="linear")

        if self.donnees.isnull().any().any():
            self.donnees = self.donnees.fillna(method="ffill").fillna(method="bfill")

        return self.donnees

    # =========================================================
    # 3. CONVERSION UNITES
    # =========================================================

    def convertir_unites(self):
        """
        Conversion typique IMU + GPS :
        - degrés → radians
        - accélération m/s² → g
        """

        import numpy as np

        # GPS (si besoin)
        if "latitude" in self.donnees.columns:
            self.donnees["latitude"] = np.radians(self.donnees["latitude"])
        if "longitude" in self.donnees.columns:
            self.donnees["longitude"] = np.radians(self.donnees["longitude"])

        # IMU acceleration (m/s² → g)
        for col in ["ax", "ay", "az"]:
            if col in self.donnees.columns:
                self.donnees[col] = self.donnees[col] / 9.81

        return self.donnees

    # =========================================================
    # 4. SYNCHRONISATION GPS / IMU
    # =========================================================

    def synchroniser(self, freq="100ms"):
        """
        Synchronisation temporelle via timestamp.

        Hypothèse :
        - GPS plus lent
        - IMU plus rapide

        On resample sur une base commune.
        """

        self.donnees["timestamp"] = pd.to_datetime(self.donnees["timestamp"])
        self.donnees = self.donnees.set_index("timestamp")

        # resampling temporel
        self.donnees = self.donnees.resample(freq).mean()

        # interpolation après resample
        self.donnees = self.donnees.interpolate()

        return self.donnees.reset_index()

    # =========================================================
    # 5. NORMALISATION
    # =========================================================

    def normaliser(self):
        """
        Normalisation Min-Max.
        """

        colonnes = self.donnees.select_dtypes(include="number").columns

        for col in colonnes:
            min_val = self.donnees[col].min()
            max_val = self.donnees[col].max()

            if max_val != min_val:
                self.donnees[col] = (self.donnees[col] - min_val) / (max_val - min_val)

        return self.donnees

    # =========================================================
    # 6. EXPORT HDF5 : plus précise
    # =========================================================
    
    def sauvegarder_hdf5(self, chemin, cle="donnees"):
        self.donnees.to_hdf(chemin, key=cle, mode="w")

    @staticmethod
    def charger_hdf5(chemin, cle="donnees"):
        return pd.read_hdf(chemin, key=cle)

    # =========================================================
    # GETTER FINAL
    # =========================================================

    def obtenir_donnees(self):
        return self.donnees