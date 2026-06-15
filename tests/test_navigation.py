import pandas as pd
import pytest

from gps_imu_nav.navigation import (
    build_navigation_outputs,
    compute_gps_trajectory,
    compute_imu_trajectory,
    compute_simple_fusion,
    load_navigation_dataset,
    run_navigation,
)


@pytest.fixture
def sample_navigation_df():
    return pd.DataFrame({
        "timestamp": pd.to_datetime([
            "2025-01-01 00:00:00",
            "2025-01-01 00:00:01",
            "2025-01-01 00:00:02",
        ]),
        "latitude": [45.0, 45.1, 45.2],
        "longitude": [-73.0, -73.1, -73.2],
        "altitude": [10.0, 10.1, 10.2],
        "ax_f": [1.0, 1.0, 1.0],
        "ay_f": [0.5, 0.5, 0.5],
    })


def test_load_navigation_dataset_reads_pickle(tmp_path, sample_navigation_df):
    dataset_path = tmp_path / "dataset_final.pkl"
    sample_navigation_df.to_pickle(dataset_path)

    result = load_navigation_dataset(dataset_path)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 3
    assert "latitude" in result.columns


def test_compute_gps_trajectory(sample_navigation_df):
    result = compute_gps_trajectory(sample_navigation_df)

    assert "x_gps" in result.columns
    assert "y_gps" in result.columns
    assert "z_gps" in result.columns
    assert len(result) == 3


def test_compute_imu_trajectory(sample_navigation_df):
    result = compute_imu_trajectory(sample_navigation_df)

    assert "x_imu" in result.columns
    assert "y_imu" in result.columns
    assert "vx_imu" in result.columns
    assert "vy_imu" in result.columns
    assert len(result) == 3


def test_compute_simple_fusion(sample_navigation_df):
    gps = compute_gps_trajectory(sample_navigation_df)
    imu = compute_imu_trajectory(sample_navigation_df)

    result = compute_simple_fusion(gps, imu, alpha=0.5)

    assert "x_fused" in result.columns
    assert "y_fused" in result.columns
    assert len(result) == 3


def test_build_navigation_outputs(sample_navigation_df):
    result = build_navigation_outputs(sample_navigation_df, alpha=0.7)

    assert "x_gps" in result.columns
    assert "x_imu" in result.columns
    assert "x_fused" in result.columns
    assert len(result) == 3


def test_run_navigation_returns_dataframe(tmp_path, sample_navigation_df):
    dataset_path = tmp_path / "dataset_final.pkl"
    output_path = tmp_path / "navigation_outputs.pkl"
    sample_navigation_df.to_pickle(dataset_path)

    result = run_navigation(dataset_path=dataset_path, alpha=0.7, save_output=True, output_path=output_path)

    assert isinstance(result, pd.DataFrame)
    assert output_path.exists()
    assert "x_fused" in result.columns

def test_load_navigation_dataset_raises_when_file_missing(tmp_path):
    missing_path = tmp_path / "missing_dataset.pkl"

    with pytest.raises(FileNotFoundError):
        load_navigation_dataset(missing_path)

def test_compute_gps_trajectory_sets_local_origin(sample_navigation_df):
    result = compute_gps_trajectory(sample_navigation_df)

    assert result.loc[0, "x_gps"] == pytest.approx(0.0)
    assert result.loc[0, "y_gps"] == pytest.approx(0.0)
    assert result.loc[0, "z_gps"] == pytest.approx(0.0)

def test_compute_gps_trajectory_raises_if_required_columns_missing(sample_navigation_df):
    bad_df = sample_navigation_df.drop(columns=["latitude"])

    with pytest.raises(ValueError):
        compute_gps_trajectory(bad_df)

def test_compute_imu_trajectory_returns_no_nan(sample_navigation_df):
    result = compute_imu_trajectory(sample_navigation_df)

    assert not result[["x_imu", "y_imu", "vx_imu", "vy_imu"]].isna().any().any()

def test_compute_imu_trajectory_raises_if_required_columns_missing(sample_navigation_df):
    bad_df = sample_navigation_df.drop(columns=["ax_f"])

    with pytest.raises(ValueError):
        compute_imu_trajectory(bad_df)

def test_compute_simple_fusion_starts_from_gps_reference(sample_navigation_df):
    gps = compute_gps_trajectory(sample_navigation_df)
    imu = compute_imu_trajectory(sample_navigation_df)

    result = compute_simple_fusion(gps, imu, alpha=0.7)

    assert result.loc[0, "x_fused"] == pytest.approx(result.loc[0, "x_gps"])
    assert result.loc[0, "y_fused"] == pytest.approx(result.loc[0, "y_gps"])

def test_compute_simple_fusion_returns_no_nan(sample_navigation_df):
    gps = compute_gps_trajectory(sample_navigation_df)
    imu = compute_imu_trajectory(sample_navigation_df)

    result = compute_simple_fusion(gps, imu, alpha=0.7)

    fused_columns = [col for col in ["x_fused", "y_fused", "vx_fused", "vy_fused"] if col in result.columns]
    assert not result[fused_columns].isna().any().any()

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
        "Gyro_X": [0.01, 0.02, 0.03],
        "Gyro_Y": [0.00, 0.01, 0.00],
        "Gyro_Z": [0.02, 0.01, 0.02],
    })