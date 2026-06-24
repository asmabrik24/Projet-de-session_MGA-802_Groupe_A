import numpy as np
import pandas as pd
import pytest

from gps_imu_nav.gps_outage import GPSOutageSimulator


def test_gps_outage_replaces_gps_values_with_nan():
    data = pd.DataFrame({
        "time_s": [0, 1, 2, 3, 4, 5],
        "x_gps": [10, 11, 12, 13, 14, 15],
        "y_gps": [20, 21, 22, 23, 24, 25],
        "x_imu": [100, 101, 102, 103, 104, 105],
        "y_imu": [200, 201, 202, 203, 204, 205],
    })

    simulator = GPSOutageSimulator(data)

    result = simulator.simulate_outage(
        start_time=2,
        duration=2
    )

    outage_rows = result["time_s"].between(2, 4)

    assert result.loc[outage_rows, "x_gps"].isna().all()
    assert result.loc[outage_rows, "y_gps"].isna().all()


def test_gps_outage_keeps_values_outside_outage():
    data = pd.DataFrame({
        "time_s": [0, 1, 2, 3, 4, 5],
        "x_gps": [10, 11, 12, 13, 14, 15],
        "y_gps": [20, 21, 22, 23, 24, 25],
    })

    simulator = GPSOutageSimulator(data)

    result = simulator.simulate_outage(
        start_time=2,
        duration=2
    )

    outside_rows = ~result["time_s"].between(2, 4)

    assert result.loc[outside_rows, "x_gps"].notna().all()
    assert result.loc[outside_rows, "y_gps"].notna().all()


def test_gps_outage_does_not_modify_imu_columns():
    data = pd.DataFrame({
        "time_s": [0, 1, 2, 3, 4, 5],
        "x_gps": [10, 11, 12, 13, 14, 15],
        "y_gps": [20, 21, 22, 23, 24, 25],
        "x_imu": [100, 101, 102, 103, 104, 105],
        "y_imu": [200, 201, 202, 203, 204, 205],
    })

    simulator = GPSOutageSimulator(data)

    result = simulator.simulate_outage(
        start_time=2,
        duration=2
    )

    assert result["x_imu"].equals(data["x_imu"])
    assert result["y_imu"].equals(data["y_imu"])


def test_gps_outage_raises_error_without_time_column():
    data = pd.DataFrame({
        "x_gps": [10, 11, 12],
        "y_gps": [20, 21, 22],
    })

    simulator = GPSOutageSimulator(data)

    with pytest.raises(ValueError):
        simulator.simulate_outage(
            start_time=1,
            duration=1
        )