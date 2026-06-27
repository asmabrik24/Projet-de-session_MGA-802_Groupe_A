import pytest

from gps_imu_nav.user_interface import UserInterface


# Tests unitaires de l'interface utilisateur en ligne de commande.
# Ils vérifient la validation des saisies, la gestion des valeurs par défaut
# et la cohérence des paramètres retournés selon le mode choisi.

# Fabrique un faux input() pour simuler une suite de réponses utilisateur dans les tests.
def make_input_mock(values):
    """Retourne une fonction input simulée à partir d'une liste de réponses."""
    iterator = iter(values)

    def _mock_input(_prompt=""):
        return next(iterator)

    return _mock_input


# Vérifie que les valeurs par défaut valides sont correctement acceptées.
def test_get_user_config_accepts_valid_defaults(monkeypatch):
    """Teste l'acceptation des valeurs par défaut valides."""
    ui = UserInterface()

    inputs = [
        "",   # t_start -> 0.0
        "",   # t_end -> None
        "",   # outage_start -> 30.0
        "",   # outage_duration -> 10.0
        "",   # mode -> 3 (FUSION)
        "",   # alpha -> 0.7
        "",   # show_plot -> True
        "",   # show_trajectory -> True
        "",   # show_velocities -> True
    ]

    monkeypatch.setattr("builtins.input", make_input_mock(inputs))

    config = ui.get_user_config(total_duration_s=3659.0)

    assert config["t_start"] == 0.0
    assert config["t_end"] is None
    assert config["outage_start"] == 30.0
    assert config["outage_duration"] == 10.0
    assert config["nav_mode"] == "FUSION"
    assert config["alpha"] == 0.7
    assert config["show_plot"] is True
    assert config["show_trajectory"] is True
    assert config["show_velocities"] is True


# Vérifie qu'un temps de début trop grand est refusé puis remplacé par une valeur valide.
def test_rejects_t_start_greater_than_total_duration(monkeypatch):
    """Teste le rejet d'un temps de début au-delà de la durée disponible."""
    ui = UserInterface()

    inputs = [
        "4000",  # invalide
        "100",   # valide
        "",      # t_end -> None
        "",      # outage_start
        "",      # outage_duration
        "",      # mode -> FUSION
        "",      # alpha
        "non",   # show_plot
    ]

    monkeypatch.setattr("builtins.input", make_input_mock(inputs))

    config = ui.get_user_config(total_duration_s=3659.0)

    assert config["t_start"] == 100.0


# Vérifie qu'un temps de fin invalide est refusé tant qu'il n'est pas strictement supérieur au début.
def test_rejects_t_end_less_than_or_equal_t_start(monkeypatch):
    """Teste le rejet d'un temps de fin inférieur ou égal au temps de début."""
    ui = UserInterface()

    inputs = [
        "100",   # t_start
        "50",    # invalide
        "100",   # invalide
        "200",   # valide
        "",      # outage_start
        "",      # outage_duration
        "",      # mode -> FUSION
        "",      # alpha
        "non",   # show_plot
    ]

    monkeypatch.setattr("builtins.input", make_input_mock(inputs))

    config = ui.get_user_config(total_duration_s=3659.0)

    assert config["t_start"] == 100.0
    assert config["t_end"] == 200.0


# Vérifie qu'un temps de fin au-delà de la durée disponible est refusé.
def test_rejects_t_end_greater_than_total_duration(monkeypatch):
    """Teste le rejet d'un temps de fin supérieur à la durée disponible."""
    ui = UserInterface()

    inputs = [
        "100",   # t_start
        "4000",  # invalide
        "500",   # valide
        "",      # outage_start
        "",      # outage_duration
        "",      # mode -> FUSION
        "",      # alpha
        "non",   # show_plot
    ]

    monkeypatch.setattr("builtins.input", make_input_mock(inputs))

    config = ui.get_user_config(total_duration_s=3659.0)

    assert config["t_end"] == 500.0


# Vérifie qu'un début de panne GPS hors fenêtre d'analyse est refusé.
def test_rejects_outage_start_outside_selected_window(monkeypatch):
    """Teste le rejet d'un début de panne GPS situé hors de la fenêtre choisie."""
    ui = UserInterface()

    inputs = [
        "0",     # t_start
        "100",   # t_end
        "200",   # outage_start invalide
        "50",    # outage_start valide
        "10",    # outage_duration valide
        "",      # mode -> FUSION
        "",      # alpha
        "non",   # show_plot
    ]

    monkeypatch.setattr("builtins.input", make_input_mock(inputs))

    config = ui.get_user_config(total_duration_s=3659.0)

    assert config["outage_start"] == 50.0
    assert config["outage_duration"] == 10.0


# Vérifie qu'une durée de panne GPS trop longue pour la fenêtre choisie est refusée.
def test_rejects_outage_duration_if_it_exceeds_window(monkeypatch):
    """Teste le rejet d'une durée de panne GPS qui dépasse la fenêtre d'analyse."""
    ui = UserInterface()

    inputs = [
        "0",      # t_start
        "100",    # t_end
        "95",     # outage_start
        "10",     # outage_duration invalide -> outage_end = 105
        "5",      # valide -> outage_end = 100
        "",       # mode -> FUSION
        "",       # alpha
        "non",    # show_plot
    ]

    monkeypatch.setattr("builtins.input", make_input_mock(inputs))

    config = ui.get_user_config(total_duration_s=3659.0)

    assert config["outage_start"] == 95.0
    assert config["outage_duration"] == 5.0


# Vérifie que le coefficient alpha doit rester compris entre 0 et 1.
def test_rejects_alpha_outside_zero_one(monkeypatch):
    """Teste la validation du coefficient alpha en mode fusion."""
    ui = UserInterface()

    inputs = [
        "",      # t_start
        "",      # t_end
        "",      # outage_start
        "",      # outage_duration
        "3",     # mode -> FUSION
        "1.5",   # invalide
        "-0.2",  # invalide
        "0.6",   # valide
        "non",   # show_plot
    ]

    monkeypatch.setattr("builtins.input", make_input_mock(inputs))

    config = ui.get_user_config(total_duration_s=3659.0)

    assert config["nav_mode"] == "FUSION"
    assert config["alpha"] == 0.6


# Vérifie qu'en dehors du mode fusion, les paramètres de panne et alpha sont neutralisés.
def test_non_fusion_mode_resets_outage_and_alpha(monkeypatch):
    """Teste la remise à zéro des paramètres de panne et d'alpha hors mode fusion."""
    ui = UserInterface()

    inputs = [
        "",      # t_start
        "",      # t_end
        "40",    # outage_start
        "20",    # outage_duration
        "1",     # mode -> GPS_ONLY
        "",      # show_plot -> True
        "",      # show_trajectory -> True
        "",      # show_velocities -> True
    ]

    monkeypatch.setattr("builtins.input", make_input_mock(inputs))

    config = ui.get_user_config(total_duration_s=3659.0)

    assert config["nav_mode"] == "GPS_ONLY"
    assert config["alpha"] is None
    assert config["outage_start"] == 0.0
    assert config["outage_duration"] == 0.0


# Vérifie que désactiver les graphiques désactive aussi les sous-options d'affichage.
def test_show_plot_false_disables_sub_options(monkeypatch):
    """Teste la désactivation des options d'affichage secondaires lorsque show_plot vaut False."""
    ui = UserInterface()

    inputs = [
        "",      # t_start
        "",      # t_end
        "",      # outage_start
        "",      # outage_duration
        "2",     # mode -> IMU_ONLY
        "non",   # show_plot
    ]

    monkeypatch.setattr("builtins.input", make_input_mock(inputs))

    config = ui.get_user_config(total_duration_s=3659.0)

    assert config["nav_mode"] == "IMU_ONLY"
    assert config["show_plot"] is False
    assert config["show_trajectory"] is False
    assert config["show_velocities"] is False


# Vérifie qu'un mode de navigation invalide est refusé puis corrigé par une saisie valide.
def test_rejects_invalid_navigation_mode_then_accepts_valid(monkeypatch):
    """Teste la validation du choix du mode de navigation."""
    ui = UserInterface()

    inputs = [
        "",      # t_start
        "",      # t_end
        "",      # outage_start
        "",      # outage_duration
        "9",     # mode invalide
        "2",     # mode valide -> IMU_ONLY
        "non",   # show_plot
    ]

    monkeypatch.setattr("builtins.input", make_input_mock(inputs))

    config = ui.get_user_config(total_duration_s=3659.0)

    assert config["nav_mode"] == "IMU_ONLY"