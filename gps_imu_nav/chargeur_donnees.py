"""
Module : chargeur_donnees.py
Description : Chargement robuste et validation des fichiers Excel (.xlsx) GPS et IMU.
Projet de Session - MGA802
"""

from pathlib import Path
import pandas as pd


# Classe responsable du chargement et de la validation initiale des fichiers de données.
class ChargeurDonnees:
    def __init__(self, chemin_fichier: str):
        # Conversion du chemin en objet Path puis validation immédiate du fichier.
        self.chemin_fichier = Path(chemin_fichier)
        self.donnees = None
        self._verifier_chemin()

    # Vérifie l'existence du fichier et le format minimal accepté.
    def _verifier_chemin(self):
        # Le fichier doit exister physiquement avant toute tentative de lecture.
        if not self.chemin_fichier.exists():
            raise FileNotFoundError(f"Fichier introuvable : {self.chemin_fichier}")

        # Seuls les formats CSV et Excel sont autorisés dans ce chargeur.
        if self.chemin_fichier.suffix not in [".csv", ".xlsx"]:
            raise ValueError("Format non supporté (CSV ou XLSX uniquement)")

    # Charge le fichier dans un DataFrame pandas puis effectue une validation minimale du contenu.
    def charger(self):
        # Lecture du fichier selon son extension.
        if self.chemin_fichier.suffix == ".csv":
            self.donnees = pd.read_csv(self.chemin_fichier)
        else:
            self.donnees = pd.read_excel(self.chemin_fichier)

        # Refuse un fichier sans contenu exploitable.
        if self.donnees.empty:
            raise ValueError("Fichier vide")

        # Supprime les lignes entièrement vides après lecture.
        self.donnees = self.donnees.dropna(how="all")

        return self.donnees
