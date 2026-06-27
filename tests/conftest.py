
import pandas as pd
import pytest

# Fixtures partagées pour les tests unitaires.
# Elles fournissent de petits jeux de données GPS et IMU
# simples, cohérents et faciles à réutiliser.


# Jeu de données GPS minimal pour tester le prétraitement,
# le renommage/nettoyage des colonnes et la gestion des timestamps.
@pytest.fixture
def sample_gps_df():
    """Retourne un petit DataFrame GPS de référence pour les tests."""
    return pd.DataFrame({
        "Timestamp": pd.to_datetime([
            "2025-01-01 00:00:00",
            "2025-01-01 00:00:01",
            "2025-01-01 00:00:02",
        ]),
        " latitude ": [45.5000, 45.5001, 45.5002],
        " longitude ": [-73.6000, -73.6001, -73.6002],
    })


# Jeu de données IMU minimal pour tester le prétraitement,
# les accélérations, les gyroscopes et la synchronisation temporelle.
@pytest.fixture
def sample_imu_df():
    """Retourne un petit DataFrame IMU de référence pour les tests."""
    return pd.DataFrame({
        "Timestamp": pd.to_datetime([
            "2025-01-01 00:00:00",
            "2025-01-01 00:00:01",
            "2025-01-01 00:00:02",
            "2025-01-01 00:00:03",
            "2025-01-01 00:00:04",
        ]),
        "Accel_X": [1.0, 0.0, 0.5, 0.2, 0.1],
        "Accel_Y": [0.0, 2.0, 0.5, 0.3, 0.2],
        "Accel_Z": [0.0, 2.0, 0.5, 0.1, 0.2],
        "Gyro_X": [0.01, 0.02, 0.03, 0.01, 0.02],
        "Gyro_Y": [0.00, 0.01, 0.00, 0.01, 0.00],
        "Gyro_Z": [0.02, 0.01, 0.02, 0.01, 0.02],
    })