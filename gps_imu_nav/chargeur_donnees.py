"""
Module : chargeur_donnees.py
Description : Chargement et validation des fichiers Excel (.xlsx) réimportés.
Projet de Session - MGA802
"""


from pathlib import Path
import pandas as pd


class ChargeurDonnees:
    """
    Classe responsable du chargement des données GPS / IMU.
    """

    def __init__(self, chemin_fichier: str):
        self.chemin_fichier = Path(chemin_fichier)
        self.donnees = None

        self._verifier_chemin()

    def _verifier_chemin(self):
        if not self.chemin_fichier.exists():
            raise FileNotFoundError(f"Fichier introuvable : {self.chemin_fichier}")

        if self.chemin_fichier.suffix not in [".csv", ".xlsx"]:
            raise ValueError("Format non supporté (CSV ou XLSX uniquement)")

    def charger(self):
        """Charge les données."""
        if self.chemin_fichier.suffix == ".csv":
            self.donnees = pd.read_csv(self.chemin_fichier)
        else:
            self.donnees = pd.read_excel(self.chemin_fichier)

        self._valider_donnees()
        return self.donnees

    def _valider_donnees(self):
        if self.donnees is None or self.donnees.empty:
            raise ValueError("Les données sont vides")

        if self.donnees.isnull().all().any():
            raise ValueError("Certaines colonnes sont entièrement vides")

    def obtenir_donnees(self):
        return self.donnees