# -*- coding: utf-8 -*-
"""Menu utilisateur complet pour la démonstration finale."""

from __future__ import annotations
import os


class UserInterface:
    """Interface utilisateur en ligne de commande pour paramétrer l'analyse de fusion GPS/IMU."""

    def get_user_config(self) -> dict:
        print("\n====================================")
        print(" PARAMÈTRES UTILISATEUR")
        print("====================================\n")

        # 1. Sélection du fichier de données
        file_path = self._read_string("Chemin ou nom du fichier CSV à analyser", "data.csv")

        # 2. Fenêtre temporelle d'analyse
        print("\n--- Fenêtre temporelle d'analyse ---")
        t_start = self._read_float("Temps de début (secondes)", 0.0)
        t_end = self._read_float("Temps de fin (secondes, 0 = fin du fichier)", 0.0)

        # 3. Paramètres de la panne GPS simulée
        print("\n--- Simulation de panne GPS ---")
        outage_start = self._read_float("Début de la panne GPS (secondes)", 30.0)
        outage_duration = self._read_float("Durée de la panne GPS (secondes)", 10.0)

        # 4. Sélection du mode de navigation
        print("\n--- Mode de navigation ---")
        print(" 1 : GPS seul")
        print(" 2 : IMU seule")
        print(" 3 : GPS/IMU fusionnés")
        mode_choice = self._read_int_range("Sélectionnez le mode de navigation", 3, 1)
        
        modes_map = {1: "GPS_ONLY", 2: "IMU_ONLY", 3: "FUSION"}
        nav_mode = modes_map[mode_choice]

        # 5. Paramètre spécifique à la fusion (Alpha)
        alpha = 0.7
        if nav_mode == "FUSION":
            while True:
                alpha = self._read_float("Coefficient de fusion GPS alpha (entre 0 et 1)", 0.7)
                if 0.0 <= alpha <= 1.0:
                    break
                print("Erreur : Le coefficient de fusion doit être compris entre 0.0 et 1.0.")

        # 6. Choix des graphiques et résultats à afficher
        print("\n--- Choix de l'affichage ---")
        show_plot = self._read_bool("Afficher les graphiques à l'écran", True)
        
        show_trajectory = True
        show_velocities = True
        if show_plot:
            show_trajectory = self._read_bool("Afficher le graphique de la trajectoire", True)
            show_velocities = self._read_bool("Afficher le graphique des vitesses", True)

        return {
            "file_path": file_path,
            "t_start": t_start,
            "t_end": t_end if t_end > t_start else None,
            "outage_start": outage_start,
            "outage_duration": outage_duration,
            "nav_mode": nav_mode,
            "alpha": alpha,
            "show_plot": show_plot,
            "show_trajectory": show_trajectory,
            "show_velocities": show_velocities,
        }

    def _read_float(self, label: str, default: float) -> float:
        value = input(f"{label} [{default}] : ").strip()
        if value == "":
            return default
        try:
            return float(value)
        except ValueError:
            print(f"Saisie invalide. Valeur par défaut ({default}) appliquée.")
            return default

    def _read_string(self, label: str, default: str) -> str:
        value = input(f"{label} [{default}] : ").strip()
        if value == "":
            return default
        return value

    def _read_bool(self, label: str, default: bool) -> bool:
        default_text = "oui" if default else "non"
        value = input(f"{label} ? oui/non [{default_text}] : ").strip().lower()
        if value == "":
            return default
        return value in ["oui", "o", "yes", "y"]

    def _read_int_range(self, label: str, default: int, min_val: int) -> int:
        value = input(f"{label} [{default}] : ").strip()
        if value == "":
            return default
        try:
            ival = int(value)
            if min_val <= ival <= default:
                return ival
            print(f"Veuillez choisir un nombre entre {min_val} et {default}.")
            return default
        except ValueError:
            return default