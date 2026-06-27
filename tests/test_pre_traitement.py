import numpy as np
import pandas as pd

from gps_imu_nav.pre_traitement import (
    preprocess_gps,
    preprocess_imu,
    synchronize_data,
)

# Tests unitaires du module de prétraitement.
# Ils vérifient le nettoyage des colonnes GPS, le calcul des grandeurs IMU
# et la synchronisation des données GPS/IMU.


 # Vérifie que le prétraitement GPS supprime correctement les espaces dans les noms de colonnes.
def test_preprocess_gps_strips_column_names(sample_gps_df):
    """Teste le nettoyage des noms de colonnes GPS."""
    result = preprocess_gps(sample_gps_df)

    assert "latitude" in result.columns
    assert "longitude" in result.columns
    assert " latitude " not in result.columns
    assert " longitude " not in result.columns



# Vérifie que le prétraitement IMU ajoute bien la norme de l'accélération filtrée.
def test_preprocess_imu_adds_acc_norm(sample_imu_df):
    """Teste l'ajout de la colonne acc_norm lors du prétraitement IMU."""
    result = preprocess_imu(sample_imu_df)

    assert "acc_norm" in result.columns
    assert len(result) == 5

    expected_first = np.sqrt(
        result.loc[0, "ax_f"] ** 2 +
        result.loc[0, "ay_f"] ** 2 +
        result.loc[0, "az_f"] ** 2
    )
    assert np.isclose(result.loc[0, "acc_norm"], expected_first)



# Vérifie que la synchronisation GPS/IMU retourne un DataFrame fusionné non vide.
def test_synchronize_data_returns_dataframe(sample_gps_df, sample_imu_df):
    """Teste la synchronisation conjointe des données GPS et IMU."""
    gps = preprocess_gps(sample_gps_df)
    imu = preprocess_imu(sample_imu_df)

    result = synchronize_data(gps, imu)

    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert "latitude" in result.columns
    assert "longitude" in result.columns
    assert "acc_norm" in result.columns



# Vérifie que la synchronisation sans IMU retourne uniquement les données GPS exploitables.
def test_synchronize_data_without_imu_returns_gps_only(sample_gps_df):
    """Teste le comportement de synchronisation lorsqu'aucune donnée IMU n'est fournie."""
    gps = preprocess_gps(sample_gps_df)

    result = synchronize_data(gps, None)

    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert "latitude" in result.columns
    assert "longitude" in result.columns