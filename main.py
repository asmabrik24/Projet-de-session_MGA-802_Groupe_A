import pandas as pd
import os

from gps_imu_nav.pre_traitement import (
    preprocess_gps,
    preprocess_imu,
    synchronize_data
)

# =========================================================
#                DESCRIPTION DU PROJET
# =========================================================
"""
 Fusion GPS + IMU

Objectif :
    Ce projet vise à traiter et fusionner des données issues de capteurs GPS et IMU.
    Le pipeline permet de nettoyer, synchroniser et structurer les données pour analyse.

Démarche générale :
    1. Chargement des données GPS et IMU
    2. Vérification et validation des fichiers
    3. Prétraitement des signaux (filtrage, nettoyage, conversion)
    4. Synchronisation temporelle GPS / IMU
    5. Construction d’un dataset final exploitable
    6. Export des données en formats CSV et Pickle
"""

# =========================================================
#                     PIPELINE PRINCIPAL
# =========================================================

def main():

    # =====================================================
    # 0. DÉFINITION DES CHEMINS
    # =====================================================
    # Centralisation des chemins pour faciliter la maintenance
    # On part du dossier contenant ce fichier `main.py` pour rendre le projet portable.
    project_root = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.join(project_root, "données")

    path_gps = os.path.join(base_path, "gps_locatisation.xlsx")
    path_imu = os.path.join(base_path, "IMUAcquisition.xlsx")

    # =====================================================
    # 1. EN-TÊTE DU PIPELINE
    # =====================================================
    print("\n====================================")
    print(" PIPELINE FUSION GPS + IMU")
    print("====================================\n")
    print(f"[INFO] Dossier projet : {project_root}")
    print(f"[INFO] Dossier données : {base_path}\n")

    # =====================================================
    # 2. CHARGEMENT DES DONNÉES BRUTES
    # =====================================================
    # Objectif : lire les fichiers Excel et vérifier leur existence

    print("[1] Chargement des données...")

    # ---- GPS ----
    if not os.path.exists(path_gps):
        print(f"[ERROR] Fichier GPS introuvable : {path_gps}")
        return

    gps = pd.read_excel(path_gps)
    print(f"[OK] GPS chargé | Shape : {gps.shape}")

    # ---- IMU ----
    imu = None
    if os.path.exists(path_imu):
        imu = pd.read_excel(path_imu)
        print(f"[OK] IMU chargé | Shape : {imu.shape}")

        # Debug important pour validation des colonnes IMU
        print("[DEBUG] Colonnes IMU :", list(imu.columns))
    else:
        print(f"[WARN] IMU absent → traitement GPS uniquement | chemin attendu : {path_imu}")

    # =====================================================
    # 3. PRÉTRAITEMENT DES DONNÉES GPS
    # =====================================================
    # Objectif : nettoyage, validation et conversion des coordonnées

    print("\n[2] Prétraitement GPS...")
    gps = preprocess_gps(gps)
    print("[OK] GPS nettoyé et structuré")

    # =====================================================
    # 4. PRÉTRAITEMENT DES DONNÉES IMU
    # =====================================================
    # Objectif : filtrage du bruit et extraction de l'accélération

    if imu is not None:
        try:
            print("[2] Prétraitement IMU...")
            imu = preprocess_imu(imu)
            print("[OK] IMU nettoyé et structuré")
        except Exception as e:
            print("[ERROR] Échec preprocessing IMU :", e)
            imu = None

    # =====================================================
    # 5. SYNCHRONISATION DES CAPTEURS
    # =====================================================
    # Objectif : aligner GPS et IMU selon le timestamp

    print("\n[3] Synchronisation GPS + IMU...")
    data = synchronize_data(gps, imu)
    print("[OK] Synchronisation terminée")

    # =====================================================
    # 6. NETTOYAGE FINAL DU DATASET
    # =====================================================
    # Objectif : supprimer doublons et organiser les données

    print("\n[4] Nettoyage final du dataset...")

    data = data.drop_duplicates()

    if "timestamp" in data.columns:
        data = data.sort_values("timestamp")

    data = data.reset_index(drop=True)

    print("[OK] Dataset final structuré")

    # =====================================================
    # 7. AFFICHAGE DES RÉSULTATS
    # =====================================================
    # Objectif : vérifier la qualité du dataset final

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

    # =====================================================
    # 8. SAUVEGARDE DES DONNÉES (CSV + PICKLE)
    # =====================================================
    # Objectif : rendre le dataset réutilisable

    print("\n[5] Sauvegarde du dataset...")

    # -----------------------------------------------------
    # CSV (format lisible pour Excel )
    # -----------------------------------------------------
    output_csv = os.path.join(base_path, "dataset_final.csv")

    data.to_csv(
        output_csv,
        index=False,
        float_format="%.6f"  # précision GPS / IMU
    )

    print(f"[SAVE] CSV sauvegardé : {output_csv}")

    # -----------------------------------------------------
    # PICKLE (format binaire pour Python )
    # -----------------------------------------------------
    # Le pickle permet de sauvegarder le DataFrame tel quel
    # (types, structure, colonnes intactes)

    output_pkl = os.path.join(base_path, "dataset_final.pkl")

    data.to_pickle(output_pkl)

    print(f"[SAVE] Pickle sauvegardé : {output_pkl}")

    # =====================================================
    # 9. FIN DU PIPELINE
    # =====================================================

    print("\n====================================")
    print("PIPELINE TERMINÉ AVEC SUCCÈS")
    print("====================================\n")


# =========================================================
#                     EXECUTION
# =========================================================

if __name__ == "__main__":
    main()