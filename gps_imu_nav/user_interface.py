# -*- coding: utf-8 -*-
"""Menu utilisateur pour la demonstration finale."""

from __future__ import annotations


class UserInterface:
    """Interface simple pour parametrer l'analyse."""

    def get_user_config(self) -> dict:
        print("\n====================================")
        print(" PARAMETRES UTILISATEUR")
        print("====================================\n")

        outage_start = self._read_float("Debut de la panne GPS en secondes", 30.0)
        outage_duration = self._read_float("Duree de la panne GPS en secondes", 10.0)
        alpha = self._read_float("Coefficient de confiance GPS alpha", 0.7)
        show_plot = self._read_bool("Afficher les graphiques a l'ecran", True)

        return {
            "outage_start": outage_start,
            "outage_duration": outage_duration,
            "alpha": alpha,
            "show_plot": show_plot,
        }

    def _read_float(self, label: str, default: float) -> float:
        value = input(f"{label} [{default}] : ").strip()
        if value == "":
            return default
        return float(value)

    def _read_bool(self, label: str, default: bool) -> bool:
        default_text = "oui" if default else "non"
        value = input(f"{label} ? oui/non [{default_text}] : ").strip().lower()
        if value == "":
            return default
        return value in ["oui", "o", "yes", "y"]
