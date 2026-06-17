# -*- coding: utf-8 -*-
"""
user_interface.py

Gestion complète des saisies et des exceptions.
"""

from __future__ import annotations

import os


class UserInterface:
    """
    Interface utilisateur en ligne de commande.
    Permet de configurer l'analyse avant l'exécution.
    """

    def get_user_config(self) -> dict:
        """
        Récupère et valide tous les paramètres utilisateur.

        Returns
        -------
        dict
            Dictionnaire de configuration.
        """

        print("\n====================================")
        print(" PARAMÈTRES UTILISATEUR")
        print("====================================")

        # --------------------------------------------------
        # Fichier CSV
        # --------------------------------------------------

        print("\n--- Sélection du fichier ---")

        while True:

            file_path = self._read_string(
                "Chemin du fichier CSV",
                "data.csv"
            )

            if not os.path.exists(file_path):
                print(
                    f"[ERREUR] Le fichier '{file_path}' est introuvable."
                )
                continue

            if not file_path.lower().endswith(".csv"):
                print(
                    "[ERREUR] Le fichier doit être au format CSV."
                )
                continue

            break

        # --------------------------------------------------
        # Fenêtre temporelle
        # --------------------------------------------------

        print("\n--- Fenêtre temporelle ---")

        while True:

            t_start = self._read_float(
                "Temps de début (s)",
                0.0
            )

            if t_start >= 0:
                break

            print(
                "[ERREUR] Le temps de début doit être positif."
            )

        while True:

            t_end = self._read_float(
                "Temps de fin (s) [0 = fin du fichier]",
                0.0
            )

            if t_end == 0:
                t_end = None
                break

            if t_end > t_start:
                break

            print(
                "[ERREUR] Le temps de fin doit être supérieur au temps de début."
            )

        # --------------------------------------------------
        # Panne GPS
        # --------------------------------------------------

        print("\n--- Simulation de panne GPS ---")

        while True:

            outage_start = self._read_float(
                "Début de la panne GPS (s)",
                30.0
            )

            if outage_start >= 0:
                break

            print(
                "[ERREUR] La valeur doit être positive."
            )

        while True:

            outage_duration = self._read_float(
                "Durée de la panne GPS (s)",
                10.0
            )

            if outage_duration >= 0:
                break

            print(
                "[ERREUR] La durée doit être positive."
            )

        if t_end is not None:

            outage_end = outage_start + outage_duration

            if outage_end > t_end:

                print(
                    "[ATTENTION] La panne GPS dépasse la fenêtre d'analyse."
                )

        # --------------------------------------------------
        # Mode de navigation
        # --------------------------------------------------

        print("\n--- Mode de navigation ---")

        print("1 : GPS seul")
        print("2 : IMU seule")
        print("3 : Fusion GPS/IMU")

        mode = self._read_int_range(
            "Choix",
            min_val=1,
            max_val=3,
            default=3
        )

        nav_modes = {
            1: "GPS_ONLY",
            2: "IMU_ONLY",
            3: "FUSION"
        }

        nav_mode = nav_modes[mode]

        # --------------------------------------------------
        # Paramètre Alpha
        # --------------------------------------------------

        alpha = None

        if nav_mode == "FUSION":

            while True:

                alpha = self._read_float(
                    "Coefficient alpha [0-1]",
                    0.7
                )

                if 0.0 <= alpha <= 1.0:
                    break

                print(
                    "[ERREUR] Alpha doit être compris entre 0 et 1."
                )

        # --------------------------------------------------
        # Affichage
        # --------------------------------------------------

        print("\n--- Affichage ---")

        show_plot = self._read_bool(
            "Afficher les graphiques",
            True
        )

        show_trajectory = False
        show_velocities = False

        if show_plot:

            show_trajectory = self._read_bool(
                "Afficher la trajectoire",
                True
            )

            show_velocities = self._read_bool(
                "Afficher les vitesses",
                True
            )

        # --------------------------------------------------
        # Configuration finale
        # --------------------------------------------------

        config = {
            "file_path": file_path,
            "t_start": t_start,
            "t_end": t_end,
            "outage_start": outage_start,
            "outage_duration": outage_duration,
            "nav_mode": nav_mode,
            "alpha": alpha,
            "show_plot": show_plot,
            "show_trajectory": show_trajectory,
            "show_velocities": show_velocities,
        }

        self._display_summary(config)

        return config

    # =====================================================
    # Fonctions privées
    # =====================================================

    def _display_summary(self, config: dict) -> None:

        print("\n====================================")
        print(" CONFIGURATION SÉLECTIONNÉE")
        print("====================================")

        for key, value in config.items():
            print(f"{key:<20} : {value}")

        print("====================================")

    def _read_string(
        self,
        label: str,
        default: str
    ) -> str:

        while True:

            try:

                value = input(
                    f"{label} [{default}] : "
                ).strip()

                return value if value else default

            except KeyboardInterrupt:
                raise

            except EOFError:
                raise

    def _read_float(
        self,
        label: str,
        default: float
    ) -> float:

        while True:

            try:

                value = input(
                    f"{label} [{default}] : "
                ).strip()

                if value == "":
                    return default

                return float(value)

            except ValueError:

                print(
                    "[ERREUR] Veuillez entrer un nombre valide."
                )

            except KeyboardInterrupt:
                raise

            except EOFError:
                raise

    def _read_bool(
        self,
        label: str,
        default: bool
    ) -> bool:

        default_text = "oui" if default else "non"

        while True:

            try:

                value = input(
                    f"{label} ? (oui/non) [{default_text}] : "
                ).strip().lower()

                if value == "":
                    return default

                if value in ("oui", "o", "yes", "y"):
                    return True

                if value in ("non", "n", "no"):
                    return False

                print(
                    "[ERREUR] Répondez par oui ou non."
                )

            except KeyboardInterrupt:
                raise

            except EOFError:
                raise

    def _read_int_range(
        self,
        label: str,
        min_val: int,
        max_val: int,
        default: int
    ) -> int:

        while True:

            try:

                value = input(
                    f"{label} [{default}] : "
                ).strip()

                if value == "":
                    return default

                number = int(value)

                if min_val <= number <= max_val:
                    return number

                print(
                    f"[ERREUR] Choisissez une valeur entre "
                    f"{min_val} et {max_val}."
                )

            except ValueError:

                print(
                    "[ERREUR] Veuillez entrer un entier valide."
                )

            except KeyboardInterrupt:
                raise

            except EOFError:
                raise