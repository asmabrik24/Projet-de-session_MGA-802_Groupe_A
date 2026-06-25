# Exemple d'utilisation du programme

## Lancement

Depuis la racine du projet :

```bash
python main.py
```

Le programme affiche ensuite une série de questions permettant de configurer l'analyse.

## Exemple d'exécution

```text
====================================
 PARAMÈTRES UTILISATEUR
====================================

Temps de début (s) [0] : 0
Temps de fin (s) [0 = fin du fichier] : 3000

--- Simulation de panne GPS ---

Début de la panne GPS (s) [30] : 30
Durée de la panne GPS (s) [10] : 10

--- Mode de navigation ---

1 : GPS seul
2 : IMU seule
3 : Fusion GPS/IMU

Choix [3] : 3

Coefficient alpha [0-1] [0.7] : 0.7

--- Affichage ---

Afficher les graphiques ? (oui/non) [oui] : oui
Afficher les trajectoires ? (oui/non) [oui] : oui
Afficher les vitesses ? (oui/non) [oui] : oui
```

## Résultat obtenu

Après validation des paramètres, le programme :

1. charge les données GPS et IMU ;
2. effectue le prétraitement et la synchronisation ;
3. calcule les trajectoires GPS, IMU et Fusion GPS/IMU ;
4. simule une panne GPS de 30 s à 40 s ;
5. calcule les erreurs de position et le RMSE ;
6. génère les graphiques de validation.

L'utilisateur peut ensuite analyser :
- les trajectoires estimées ;
- les erreurs de position ;
- les valeurs du RMSE ;
- l'impact de la panne GPS sur la navigation.