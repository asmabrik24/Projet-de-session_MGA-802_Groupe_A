import numpy as np
import pandas as pd

from gps_imu_nav.pre_traitement import (
    preprocess_gps,
    preprocess_imu,
    synchronize_data,
)


def test_preprocess_gps_strips_column_names(sample_gps_df):
    result = preprocess_gps(sample_gps_df)

    assert "latitude" in result.columns
    assert "longitude" in result.columns
    assert " latitude " not in result.columns
    assert " longitude " not in result.columns


def test_preprocess_imu_adds_acc_norm(sample_imu_df):
    result = preprocess_imu(sample_imu_df)

    assert "acc_norm" in result.columns
    assert len(result) == 3

    expected_first = np.sqrt(1.0**2 + 0.0**2 + 0.0**2)
    assert np.isclose(result.loc[0, "acc_norm"], expected_first)


def test_synchronize_data_returns_dataframe(sample_gps_df, sample_imu_df):
    gps = preprocess_gps(sample_gps_df)
    imu = preprocess_imu(sample_imu_df)

    result = synchronize_data(gps, imu)

    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert "latitude" in result.columns
    assert "longitude" in result.columns
    assert "acc_norm" in result.columns


def test_synchronize_data_without_imu_returns_gps_only(sample_gps_df):
    gps = preprocess_gps(sample_gps_df)

    result = synchronize_data(gps, None)

    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert "latitude" in result.columns
    assert "longitude" in result.columns