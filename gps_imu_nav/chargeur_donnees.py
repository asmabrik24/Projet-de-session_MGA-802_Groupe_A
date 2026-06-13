"""
Module : chargeur_donnees.py
Description : Chargement robuste et validation des fichiers Excel (.xlsx) GPS et IMU.
Projet de Session - MGA802
"""

from pathlib import Path
import pandas as pd


class ChargeurDonnees:
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
        if self.chemin_fichier.suffix == ".csv":
            self.donnees = pd.read_csv(self.chemin_fichier)
        else:
            self.donnees = pd.read_excel(self.chemin_fichier)

        if self.donnees.empty:
            raise ValueError("Fichier vide")

        self.donnees = self.donnees.dropna(how="all")

        return self.donnees