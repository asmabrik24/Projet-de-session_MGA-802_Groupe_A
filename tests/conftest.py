import pandas as pd
import pytest


@pytest.fixture
def sample_gps_df():
    return pd.DataFrame({
        "Timestamp": pd.to_datetime([
            "2025-01-01 00:00:00",
            "2025-01-01 00:00:01",
            "2025-01-01 00:00:02",
        ]),
        " latitude ": [45.5000, 45.5001, 45.5002],
        " longitude ": [-73.6000, -73.6001, -73.6002],
    })


@pytest.fixture
def sample_imu_df():
    return pd.DataFrame({
        "Timestamp": pd.to_datetime([
            "2025-01-01 00:00:00",
            "2025-01-01 00:00:01",
            "2025-01-01 00:00:02",
        ]),
        "Accel_X": [1.0, 0.0, 0.5],
        "Accel_Y": [0.0, 2.0, 0.5],
        "Accel_Z": [0.0, 2.0, 0.5],
    })