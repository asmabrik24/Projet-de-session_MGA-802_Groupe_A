import pytest

from gps_imu_nav.user_interface import UserInterface


def make_input_mock(values):
    iterator = iter(values)

    def _mock_input(_prompt=""):
        return next(iterator)

    return _mock_input


def test_get_user_config_accepts_valid_defaults(monkeypatch):
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


def test_rejects_t_start_greater_than_total_duration(monkeypatch):
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


def test_rejects_t_end_less_than_or_equal_t_start(monkeypatch):
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


def test_rejects_t_end_greater_than_total_duration(monkeypatch):
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


def test_rejects_outage_start_outside_selected_window(monkeypatch):
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


def test_rejects_outage_duration_if_it_exceeds_window(monkeypatch):
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


def test_rejects_alpha_outside_zero_one(monkeypatch):
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


def test_non_fusion_mode_resets_outage_and_alpha(monkeypatch):
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


def test_show_plot_false_disables_sub_options(monkeypatch):
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


def test_rejects_invalid_navigation_mode_then_accepts_valid(monkeypatch):
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