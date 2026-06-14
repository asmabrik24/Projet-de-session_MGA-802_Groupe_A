import os
import pandas as pd

from gps_imu_nav.pre_traitement import (
    preprocess_gps,
    preprocess_imu,
    synchronize_data,
)


class FusionPipeline:
    """
    Classe responsable d'exécuter le pipeline principal GPS + IMU.
    Elle centralise le chargement, le prétraitement, la synchronisation,
    le nettoyage final et la sauvegarde des résultats.
    """

    def __init__(self) -> None:
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(self.project_root)
        self.base_path = os.path.join(self.project_root, "données")
        self.path_gps = os.path.join(self.base_path, "gps_locatisation.xlsx")
        self.path_imu = os.path.join(self.base_path, "IMUAcquisition.xlsx")

    def run(self) -> None:
        print("\n====================================")
        print(" PIPELINE FUSION GPS + IMU")
        print("====================================\n")
        print(f"[INFO] Dossier projet : {self.project_root}")
        print(f"[INFO] Dossier données : {self.base_path}\n")

        print("[1] Chargement des données...")

        if not os.path.exists(self.path_gps):
            print(f"[ERROR] Fichier GPS introuvable : {self.path_gps}")
            return

        gps = pd.read_excel(self.path_gps)
        print(f"[OK] GPS chargé | Shape : {gps.shape}")

        imu = None
        if os.path.exists(self.path_imu):
            imu = pd.read_excel(self.path_imu)
            print(f"[OK] IMU chargé | Shape : {imu.shape}")
            print("[DEBUG] Colonnes IMU :", list(imu.columns))
        else:
            print(
                f"[WARN] IMU absent → traitement GPS uniquement | chemin attendu : {self.path_imu}"
            )

        print("\n[2] Prétraitement GPS...")
        gps = preprocess_gps(gps)
        print("[OK] GPS nettoyé et structuré")

        if imu is not None:
            try:
                print("[2] Prétraitement IMU...")
                imu = preprocess_imu(imu)
                print("[OK] IMU nettoyé et structuré")
            except Exception as e:
                print("[ERROR] Échec preprocessing IMU :", e)
                imu = None

        print("\n[3] Synchronisation GPS + IMU...")
        data = synchronize_data(gps, imu)
        print("[OK] Synchronisation terminée")

        print("\n[4] Nettoyage final du dataset...")
        data = data.drop_duplicates()

        if "timestamp" in data.columns:
            data = data.sort_values("timestamp")

        data = data.reset_index(drop=True)
        print("[OK] Dataset final structuré")

        print("\n====================================")
        print("RÉSULTATS FINAUX")
        print("====================================\n")

        print(f" Shape finale : {data.shape}\n")
        print(" Aperçu des données :")
        print(data.head(10))

        print("\n Colonnes disponibles :")
        print(list(data.columns))

        print("\n Statistiques GPS :")
        print(data[["latitude", "longitude"]].describe())

        if "acc_norm" in data.columns:
            print("\n Statistiques IMU (acc_norm) :")
            print(data["acc_norm"].describe())

        print("\n[5] Sauvegarde du dataset...")

        output_csv = os.path.join(self.base_path, "dataset_final.csv")
        data.to_csv(output_csv, index=False, float_format="%.6f")
        print(f"[SAVE] CSV sauvegardé : {output_csv}")

        output_pkl = os.path.join(self.base_path, "dataset_final.pkl")
        data.to_pickle(output_pkl)
        print(f"[SAVE] Pickle sauvegardé : {output_pkl}")

        print("\n====================================")
        print("PIPELINE TERMINÉ AVEC SUCCÈS")
        print("====================================\n")