
# Projet de session MGA802_Groupe_A - Fusion GPS/IMU pour la navigation véhiculaire à l’aide de Python.
---
# Description du projet

Ce projet vise à développer une bibliothèque Python permettant d'estimer la trajectoire d'un véhicule à partir de données GPS et IMU.

L'objectif principal est de comparer trois approches de navigation :

* GPS seul
* IMU seule
* Fusion GPS/IMU

Le projet permet également :

* de simuler une panne GPS ;
* d'évaluer les performances des différentes méthodes ;
* de calculer les erreurs de position ;
* de calculer le RMSE ;
* de générer des graphiques de validation.
---
# Structure du projet

```text

Projet-de-session_MGA-802_Groupe_A/
│
├── données/
│
├── figures/
│   
├── gps_imu_nav/
│   ├── chargeur_donnees.py
│   ├── pipeline.py
│   ├── pre_traitement.py
│   ├── navigation.py
│   ├── gps_outage.py
│   ├── evaluator.py
│   ├── graphique.py
│   ├── user_interface.py
│   └── visualization.py
│
├── tests/
│   ├── test_pipeline.py
│   ├── test_pre_traitement.py
│   ├── test_navigation.py
│   ├── test_gps_outage.py
│   ├── test_user_interface.py
│   └── test_visualization.py
│
├── app.py
├── main.py
├── README.md
├── requirements.txt
└── .gitignore
```
| Module              | Rôle                                                     |
| ------------------- | -------------------------------------------------------- |
| Main.py             | Point d'entrée du programme                              |
| User_interface.py   | Gestion des paramètres utilisateur                       |
| Pipeline.py         | Exécution du pipeline complet                            |
| Chargeur_donnees.py | Chargement et validation des données                     |
| Pre_traitement.py   | Nettoyage et synchronisation                             |
| Navigation.py       | Calcul des trajectoires GPS, IMU et Fusion               |
| GPS_outage.py       | Simulation de panne GPS                                  |
| Evaluator.py        | Calcul des erreurs et du RMSE                            |
| Visualization.py    | Génération des graphiques et visualisation des résultats |

---
# Architecture orientée objet

Le projet est développé selon une architecture orientée objet afin de séparer les responsabilités et faciliter la maintenance du code.

## Classes principales

| Classe              | Rôle                       |
| ------------------- | -------------------------- |
| ChargeurDonnees     | Chargement des données     |
| FusionPipeline      | Pipeline complet           |
| GPSOutageSimulator  | Simulation de panne GPS    |
| TrajectoryEvaluator | Calcul des erreurs et RMSE |
| UserInterface       | Paramètres utilisateur     |

---

# Méthodes de navigation

## GPS seul

La trajectoire est calculée uniquement à partir des mesures GPS.

### Avantages

* Position absolue précise
* Faible dérive

### Limites

* Sensible aux pertes de signal

---

## IMU seule

La trajectoire est calculée à partir des accélérations mesurées par l'IMU.

### Avantages

* Fonctionnement continu
* Fréquence d'acquisition élevée

### Limites

* Accumulation des erreurs
* Dérive au cours du temps

---

## Fusion GPS/IMU

Le projet implémente une fusion pondérée :

Position_fusion = α × Position_GPS + (1 − α) × Position_IMU

avec :

α = 0,7

Le GPS est considéré comme plus fiable pour la position absolue tandis que l'IMU assure la continuité de la navigation.

---

# Fonctionnalités

- Chargement des données GPS et IMU
- Validation des fichiers
- Prétraitement des données
- Synchronisation GPS/IMU
- Calcul de trajectoires GPS seules
- Calcul de trajectoires IMU seules
- Fusion GPS/IMU
- Simulation de panne GPS
- Calcul des erreurs de position
- Calcul du RMSE
- Visualisation des trajectoires
- Analyse de la dérive IMU
- Analyse des vitesses estimées
- Interface utilisateur interactive

---

# Bibliothèques utilisées

* Pandas
* NumPy
* Matplotlib
* PyTest
* Sphinx

---

# Installation

Créer un environnement virtuel :

```bash
python -m venv .venv
```

Activer l'environnement :

```bash
.venv\Scripts\activate
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

---

# Exécution du programme

Lancer :

```bash
python main.py
```

Le programme permet notamment de configurer :

* le début de la panne GPS ;
* la durée de la panne GPS ;
* le coefficient de fusion α ;
* le mode de navigation ;
* l'affichage des graphiques.

---

# Tests unitaires

Le projet contient plusieurs tests unitaires développés avec PyTest.

## Modules testés

| Fichier de test        | Fonction vérifiée                     |
| ---------------------- | ------------------------------------- |
| test_pipeline.py       | Exécution du pipeline                 |
| test_pre_traitement.py | Prétraitement et synchronisation      |
| test_navigation.py     | Calcul des trajectoires               |
| test_gps_outage.py     | Simulation de panne GPS               |
| test_user_interface.py | Validation des paramètres utilisateur |
| test_visualization.py  | Génération des graphiques             |

## Exécution des tests

```bash
pytest tests/
```

Exemple de résultat :

```text
=============================
4 tests passed
=============================
```

---

# Vérification et validation

La validation du projet repose sur :

* la comparaison des trajectoires GPS, IMU et fusionnées ;
* l'analyse des erreurs de position ;
* le calcul du RMSE ;
* la simulation de pannes GPS ;
* les tests unitaires automatisés.

Les résultats montrent que :

* l'IMU seule présente une dérive importante ;
* la fusion GPS/IMU améliore significativement la précision ;
* la navigation reste fonctionnelle lors d'une perte temporaire du signal GPS.

---

# Documentation Sphinx

La documentation HTML est générée automatiquement à partir des docstrings présentes dans le code.

Génération :

```bash
sphinx-build -b html docs docs/_build/html
```

Le résultat est disponible dans :

```text
docs/_build/html/index.html
```

---

# Travaux restants et améliorations futures

* Tester le système sur plusieurs jeux de données.
* Simuler différents scénarios de panne GPS.
* Remplacer la fusion pondérée par un filtre de Kalman.
* Développer une interface graphique interactive avec Streamlit.

---

# Auteurs

- Asma BRIK
- Brahim REZGUI
- Nada CHAOUACHI

