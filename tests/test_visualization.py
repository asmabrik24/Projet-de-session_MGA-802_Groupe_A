import pandas as pd
import pytest

from gps_imu_nav.visualization import (
    plot_gps_trajectory_only,
    plot_trajectories,
    plot_velocities,
    summarize_navigation_results,
    validate_navigation_results,
)


@pytest.fixture
def sample_navigation_results():
    return pd.DataFrame({
        "time_s": [0.0, 1.0, 2.0, 3.0, 4.0],
        "x_gps": [0.0, 10.0, 20.0, 30.0, 40.0],
        "y_gps": [0.0, 5.0, 11.0, 18.0, 26.0],
        "x_imu": [0.0, 9.0, 22.0, 35.0, 48.0],
        "y_imu": [0.0, 4.0, 13.0, 25.0, 40.0],
        "x_fused": [0.0, 9.5, 20.5, 31.0, 41.0],
        "y_fused": [0.0, 4.5, 11.8, 19.2, 27.0],
        "vx_imu": [0.5, 0.7, 0.8, 0.9, 1.0],
        "vy_imu": [0.2, 0.3, 0.4, 0.5, 0.6],
        "vx_fused": [0.5, 0.6, 0.7, 0.8, 0.9],
        "vy_fused": [0.2, 0.25, 0.35, 0.45, 0.55],
    })


def test_validate_navigation_results_accepts_valid_dataframe(sample_navigation_results):
    validate_navigation_results(sample_navigation_results)


def test_validate_navigation_results_raises_when_columns_missing(sample_navigation_results):
    bad_df = sample_navigation_results.drop(columns=["x_fused"])

    with pytest.raises(ValueError):
        validate_navigation_results(bad_df)


def test_plot_gps_trajectory_only_creates_png(tmp_path, sample_navigation_results):
    output_path = tmp_path / "gps_only.png"

    result = plot_gps_trajectory_only(
        sample_navigation_results,
        save_figure=True,
        output_path=output_path,
        show_plot=False,
    )

    assert result == output_path
    assert output_path.exists()


def test_plot_trajectories_creates_focused_png(tmp_path, sample_navigation_results):
    output_path = tmp_path / "gps_fusion.png"

    result = plot_trajectories(
        sample_navigation_results,
        save_figure=True,
        output_path=output_path,
        show_plot=False,
    )

    assert result == output_path
    assert output_path.exists()


def test_plot_velocities_creates_png(tmp_path, sample_navigation_results):
    output_path = tmp_path / "velocities.png"

    result = plot_velocities(
        sample_navigation_results,
        save_figure=True,
        output_path=output_path,
        show_plot=False,
    )

    assert result == output_path
    assert output_path.exists()


def test_plot_velocities_raises_when_columns_missing(sample_navigation_results):
    bad_df = sample_navigation_results.drop(columns=["vx_imu"])

    with pytest.raises(ValueError):
        plot_velocities(bad_df, save_figure=False, show_plot=False)


def test_summarize_navigation_results_returns_three_modes(sample_navigation_results):
    summary = summarize_navigation_results(sample_navigation_results)

    assert list(summary["mode"]) == ["GPS", "IMU", "Fusion"]
    assert len(summary) == 3
    assert "x_final_m" in summary.columns
    assert "y_final_m" in summary.columns


def test_summarize_navigation_results_uses_last_row_values(sample_navigation_results):
    summary = summarize_navigation_results(sample_navigation_results)

    gps_row = summary.loc[summary["mode"] == "GPS"].iloc[0]
    imu_row = summary.loc[summary["mode"] == "IMU"].iloc[0]
    fusion_row = summary.loc[summary["mode"] == "Fusion"].iloc[0]

    assert gps_row["x_final_m"] == pytest.approx(40.0)
    assert gps_row["y_final_m"] == pytest.approx(26.0)
    assert imu_row["x_final_m"] == pytest.approx(48.0)
    assert imu_row["y_final_m"] == pytest.approx(40.0)
    assert fusion_row["x_final_m"] == pytest.approx(41.0)
    assert fusion_row["y_final_m"] == pytest.approx(27.0)