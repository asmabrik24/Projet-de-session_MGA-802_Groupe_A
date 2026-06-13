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

    Objectif :
    - centraliser l'accès aux fichiers de données
    - garantir la validité des fichiers
    - éviter les erreurs en amont du pipeline
    """

    def __init__(self, chemin_fichier: str):
        # Conversion en Path pour une meilleure gestion des chemins
        self.chemin_fichier = Path(chemin_fichier)

        # Stockage des données après chargement
        self.donnees = None

        # Validation immédiate du fichier dès l'initialisation
        self._verifier_chemin()

    def _verifier_chemin(self):
        """
        Vérifie que :
        - le fichier existe
        - le format est supporté
        """

        if not self.chemin_fichier.exists():
            raise FileNotFoundError(
                f"Erreur : fichier introuvable -> {self.chemin_fichier}"
            )

        # On limite volontairement les formats pour simplifier le pipeline
        if self.chemin_fichier.suffix not in [".csv", ".xlsx"]:
            raise ValueError(
                "Format non supporté. Utiliser CSV ou XLSX uniquement."
            )

    def charger(self):
        """
        Charge les données selon le type de fichier.

        Retour :
        - DataFrame pandas contenant les données brutes
        """

        # Lecture conditionnelle selon extension
        if self.chemin_fichier.suffix == ".csv":
            self.donnees = pd.read_csv(self.chemin_fichier)

        else:
            self.donnees = pd.read_excel(self.chemin_fichier)

        # Validation après chargement pour garantir intégrité
        self._valider_donnees()

        return self.donnees

    def _valider_donnees(self):
        """
        Vérifie la qualité minimale des données :
        - non vide
        - colonnes non totalement nulles
        """

        if self.donnees is None or self.donnees.empty:
            raise ValueError("Les données chargées sont vides")

        # Détection de colonnes totalement invalides
        if self.donnees.isnull().all().any():
            raise ValueError(
                "Certaines colonnes contiennent uniquement des valeurs nulles"
            )

    def obtenir_donnees(self):
        """
        Accées aux données chargées.
        """
        return self.donnees