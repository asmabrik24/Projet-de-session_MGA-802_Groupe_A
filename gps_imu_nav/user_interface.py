# -*- coding: utf-8 -*-
"""
user_interface.py

Gestion complète des saisies et des exceptions.
"""

from __future__ import annotations


class UserInterface:
    """
    Interface utilisateur en ligne de commande.
    Permet de configurer l'analyse avant l'exécution.
    """

    def get_user_config(self, total_duration_s: float | None = None) -> dict:
        """
        Récupère et valide tous les paramètres utilisateur.

        Returns
        -------
        dict
            Dictionnaire de configuration.

        Parameters
        ----------
        total_duration_s : float | None
            Durée maximale disponible de la trajectoire en secondes.
            Si fournie, les saisies utilisateur sont validées par rapport
            à cette borne.
        """

        print("\n====================================")
        print(" PARAMÈTRES UTILISATEUR")
        print("====================================")

        if total_duration_s is not None:
            print(f"[INFO] Durée disponible de la trajectoire : {total_duration_s:.3f} s")

        # --------------------------------------------------
        # Fenêtre temporelle
        # --------------------------------------------------

        print("\n--- Fenêtre temporelle ---")

        while True:

            t_start = self._read_float(
                "Temps de début (s)",
                0.0
            )

            if t_start < 0:
                print(
                    "[ERREUR] Le temps de début doit être positif."
                )
                continue

            if total_duration_s is not None and t_start > total_duration_s:
                print(
                    f"[ERREUR] Le temps de début dépasse la durée disponible ({total_duration_s:.3f} s)."
                )
                continue

            break

        while True:

            t_end = self._read_float(
                "Temps de fin (s) [0 = fin du fichier]",
                0.0
            )

            if t_end == 0:
                t_end = None
                break

            if t_end <= t_start:
                print(
                    "[ERREUR] Le temps de fin doit être supérieur au temps de début."
                )
                continue

            if total_duration_s is not None and t_end > total_duration_s:
                print(
                    f"[ERREUR] Le temps de fin dépasse la durée disponible ({total_duration_s:.3f} s)."
                )
                continue

            break

        # --------------------------------------------------
        # Simulation de panne GPS
        # --------------------------------------------------

        print("\n--- Simulation de panne GPS ---")

        outage_start = 30.0
        outage_duration = 10.0

        while True:

            outage_start = self._read_float(
                "Début de la panne GPS (s)",
                30.0
            )

            if outage_start < 0:
                print(
                    "[ERREUR] Le début de la panne GPS doit être positif."
                )
                continue

            if total_duration_s is not None and outage_start > total_duration_s:
                print(
                    f"[ERREUR] Le début de la panne GPS dépasse la durée disponible ({total_duration_s:.3f} s)."
                )
                continue

            if t_end is not None and outage_start > t_end:
                print(
                    "[ERREUR] Le début de la panne GPS doit être inclus dans la fenêtre d'analyse."
                )
                continue

            break

        while True:

            outage_duration = self._read_float(
                "Durée de la panne GPS (s)",
                10.0
            )

            if outage_duration < 0:
                print(
                    "[ERREUR] La durée de la panne GPS doit être positive."
                )
                continue

            outage_end = outage_start + outage_duration

            if total_duration_s is not None and outage_end > total_duration_s:
                print(
                    f"[ERREUR] La panne GPS dépasse la durée disponible ({total_duration_s:.3f} s)."
                )
                continue

            if t_end is not None and outage_end > t_end:
                print(
                    "[ERREUR] La panne GPS dépasse la fenêtre d'analyse choisie."
                )
                continue

            break

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

        print(f"[INFO] Mode sélectionné : {nav_mode}")

        # --------------------------------------------------
        # Paramètre Alpha
        # --------------------------------------------------

        alpha = None

        if nav_mode == "FUSION":
            # Alpha ne s'applique qu'au mode fusion.

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
                "Afficher les trajectoires",
                True
            )

            show_velocities = self._read_bool(
                "Afficher les vitesses",
                True
            )

        if nav_mode != "FUSION":
            outage_start = 0.0
            outage_duration = 0.0
            print("[INFO] Les paramètres de panne GPS sont ignorés hors mode FUSION.")

        # --------------------------------------------------
        # Configuration finale
        # --------------------------------------------------

        config = {

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
            label = key.replace("_", " ")
            print(f"{label:<20} : {value}")

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
