
import os
import pandas as pd

from gps_imu_nav.pipeline import FusionPipeline

# Tests unitaires du pipeline principal.
# Ils vérifient la création des fichiers de sortie dans un dossier temporaire,
# avec et sans fichier IMU disponible.

# Vérifie que l'exécution complète du pipeline génère les fichiers CSV et Pickle attendus.
def test_pipeline_run_creates_output_files(tmp_path):
    """Teste que le pipeline crée les fichiers de sortie principaux."""
    # Création d'une structure de projet temporaire avec un jeu de données minimal.
    project_root = tmp_path
    data_dir = project_root / "données"
    data_dir.mkdir()

    gps_df = pd.DataFrame({
        "Timestamp": pd.to_datetime([
            "2025-01-01 00:00:00",
            "2025-01-01 00:00:01",
            "2025-01-01 00:00:02",
        ]),
        " latitude ": [45.5000, 45.5001, 45.5002],
        " longitude ": [-73.6000, -73.6001, -73.6002],
    })

    imu_df = pd.DataFrame({
        "Timestamp": pd.to_datetime([
            "2025-01-01 00:00:00",
            "2025-01-01 00:00:01",
            "2025-01-01 00:00:02",
        ]),
        "Accel_X": [1.0, 0.0, 0.5],
        "Accel_Y": [0.0, 2.0, 0.5],
        "Accel_Z": [0.0, 2.0, 0.5],
    })

    gps_path = data_dir / "gps_locatisation.xlsx"
    imu_path = data_dir / "IMUAcquisition.xlsx"

    gps_df.to_excel(gps_path, index=False)
    imu_df.to_excel(imu_path, index=False)

    pipeline = FusionPipeline()

    # Redirige les chemins internes du pipeline vers le dossier temporaire de test.
    pipeline.project_root = str(project_root)
    pipeline.base_path = str(data_dir)
    pipeline.path_gps = str(gps_path)
    pipeline.path_imu = str(imu_path)

    pipeline.run()

    output_csv = data_dir / "dataset_final.csv"
    output_pkl = data_dir / "dataset_final.pkl"

    assert output_csv.exists()
    assert output_pkl.exists()

# Vérifie que le pipeline reste capable de produire un CSV même si le fichier IMU est absent.
def test_pipeline_run_without_imu_still_creates_csv(tmp_path):
    """Teste le comportement du pipeline lorsque les données IMU ne sont pas disponibles."""
    project_root = tmp_path
    data_dir = project_root / "données"
    data_dir.mkdir()

    gps_df = pd.DataFrame({
        "Timestamp": pd.to_datetime([
            "2025-01-01 00:00:00",
            "2025-01-01 00:00:01",
        ]),
        " latitude ": [45.5000, 45.5001],
        " longitude ": [-73.6000, -73.6001],
    })

    gps_path = data_dir / "gps_locatisation.xlsx"
    gps_df.to_excel(gps_path, index=False)

    pipeline = FusionPipeline()
    pipeline.project_root = str(project_root)
    pipeline.base_path = str(data_dir)
    pipeline.path_gps = str(gps_path)
    pipeline.path_imu = str(data_dir / "IMUAcquisition.xlsx")  # fichier absent volontairement

    pipeline.run()

    output_csv = data_dir / "dataset_final.csv"
    assert output_csv.exists()