# Physics-AI-Lab: Réseau de Neurones Informé par la Physique (PINN) de Qualité Industrielle

**Accélérer les simulations physiques avec l'IA.**

Ce dépôt contient une implémentation de réseau de neurones informé par la physique (PINN) pour la résolution d'équations aux dérivées partielles (EDP), spécifiquement l'équation de Burgers 1D, l'équation de Navier-Stokes 2D et l'équation de la chaleur 2D, conçue avec des pratiques de développement logiciel de qualité industrielle. Il sert de fondation pour la recherche, de prototype pour une startup deep-tech, et de portfolio pour des applications académiques.

## Table des Matières
- [Contexte](#contexte)
- [Fonctionnalités](#fonctionnalités)
- [Structure du Projet](#structure-du-projet)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Configuration](#configuration)
- [Extension à d'Autres EDP](#extension-à-dautres-edp)
- [Pipeline de Données CFD](#pipeline-de-données-cfd)
- [Déploiement](#déploiement)
- [Tests](#tests)
- [Applications](#applications)
- [Recherche](#recherche)
- [Infrastructure](#infrastructure)
- [Licence](#licence)
- [Contact](#contact)

## Contexte
Les PINN sont une approche innovante pour résoudre des EDP en intégrant la physique du problème directement dans la fonction de perte d'un réseau de neurones. Cette implémentation vise à transformer un prototype académique en une solution robuste et évolutive adaptée aux exigences industrielles, telles que la modélisation de la dynamique des fluides (CFD), la science des matériaux ou la physique du climat.

## Fonctionnalités
Cette version industrielle du PINN inclut les améliorations suivantes :
- **Généricité des EDP** : Architecture extensible pour différentes EDP via une interface `PDE` abstraite, supportant désormais l'équation de Burgers 1D, Navier-Stokes 2D et l'équation de la chaleur 2D.
- **Gestion des Conditions aux Limites** : Intégration des conditions aux limites (Dirichlet, Neumann, etc.) dans la fonction de perte.
- **Pipeline de Données Robuste** : Utilisation de `torch.utils.data.Dataset` et `DataLoader` pour une gestion efficace des données CFD.
- **Entraînement Avancé** : Implémentation du checkpointing, de l'arrêt précoce (early stopping), et de la journalisation (logging) détaillée.
- **Échantillonnage Adaptatif** : Intégration de l'échantillonnage adaptatif pour les points de collocation PDE, permettant de concentrer les ressources de calcul dans les régions à forte erreur et d'améliorer la convergence.
- **Quantification d'Incertitude (UQ)** : Support de la quantification d'incertitude via Monte Carlo Dropout, fournissant des estimations de la confiance des prédictions du modèle.
- **Opérateurs de Neurones Informés par la Physique (PINO)** : Un placeholder pour l'intégration future des PINO, ouvrant la voie à une inférence plus rapide et à l'apprentissage d'opérateurs fonctionnels.
- **Configuration Centralisée** : Gestion des hyperparamètres et des chemins de fichiers via un fichier `config.py`.
- **Performance** : Prêt pour l'intégration de `torch.cuda.amp` (mixed precision) et `torch.compile` pour l'accélération.
- **Journalisation et Monitoring** : Utilisation du module `logging` standard de Python pour une traçabilité claire.
- **Robustesse** : Vérification des entrées et gestion des erreurs (par exemple, détection de NaN dans la perte).
- **Tests Unitaires (à implémenter)** : Cadre pour l'ajout de tests unitaires avec `pytest`.
- **Documentation** : Documentation complète du code via des docstrings et ce fichier README.
- **Dépendances Gérées** : Fichier `requirements.txt` pour un environnement reproductible.

## Structure du Projet
```
physics-ai-lab/
├── core/
│   ├── pinn_industrial.py    # Implémentation PINN de qualité industrielle (incluant PINO placeholder et UQ)
│   ├── data_pipeline.py      # Pipeline de données pour les données CFD
│   ├── ethics_validator.py   # (Fichier existant, non modifié dans cette version)
│   └── pinn_engine_original.py # Version originale de l'implémentation PINN de Burgers
├── config.py                 # Fichier de configuration pour les hyperparamètres et les chemins
├── train.py                  # Script d'entraînement principal (incluant échantillonnage adaptatif)
├── requirements.txt          # Dépendances Python
├── README.md                 # Ce fichier
└── ...                       # Autres fichiers du projet original
```

## Installation
1.  **Cloner le dépôt** :
    ```bash
    git clone <URL_DU_DÉPÔT>
    cd physics-ai-lab
    ```
2.  **Créer un environnement virtuel** (recommandé) :
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    # venv\Scripts\activate   # Windows
    ```
3.  **Installer les dépendances** :
    ```bash
    pip install -r requirements.txt
    ```

## Utilisation
Pour entraîner le modèle PINN pour l'équation de Burgers, Navier-Stokes 2D ou l'équation de la chaleur 2D :

1.  **Sélectionnez l'EDP** : Modifiez la variable `PDE_TYPE` dans `config.py` (`burgers`, `navier_stokes_2d`, `heat_equation_2d` ou `pino_placeholder`).
2.  **Exécutez l'entraînement** :
    ```bash
    python train.py
    ```

Le script `train.py` utilisera les configurations définies dans `config.py` pour générer des points de collocation, des conditions initiales et aux limites, entraîner le modèle, journaliser la progression, sauvegarder les checkpoints et le modèle final. L'échantillonnage adaptatif sera utilisé si activé dans `config.py`, et une démonstration de la quantification d'incertitude sera effectuée si le dropout est activé.

## Configuration
Le fichier `config.py` contient tous les paramètres configurables pour l'entraînement et le modèle. Voici les sections clés :

-   **`PROJECT_NAME`** : Nom du projet.
-   **`DEVICE`** : Appareil d'entraînement (`cuda` ou `cpu`).
-   **`PDE_TYPE`** : Type d'EDP à résoudre (actuellement `burgers`, `navier_stokes_2d`, `heat_equation_2d`, `pino_placeholder`).
-   **`EPOCHS`** : Nombre total d'époques d'entraînement.
-   **`LEARNING_RATE`** : Taux d'apprentissage de l'optimiseur Adam.
-   **`BATCH_SIZE`** : Taille du lot pour les points PDE, les points de données et les points de condition aux limites.
-   **`LAYERS`** : Architecture du réseau de neurones (nombre de neurones par couche), définie par `PDE_TYPE`.
-   **`ACTIVATION`** : Fonction d'activation (`tanh`, `relu`, etc.).
-   **`USE_BATCH_NORM`** : Active/désactive la normalisation par lots.
-   **`USE_DROPOUT`** : Active/désactive le dropout pour la quantification d'incertitude.
-   **`DROPOUT_RATE`** : Taux de dropout.
-   **`BURGERS_NU`** : Paramètre `nu` pour l'équation de Burgers.
-   **`NAVIER_STOKES_NU`, `NAVIER_STOKES_RHO`** : Paramètres pour l'équation de Navier-Stokes 2D.
-   **`HEAT_CONDUCTIVITY`, `HEAT_DENSITY`, `HEAT_SPECIFIC_HEAT`** : Paramètres pour l'équation de la chaleur 2D.
-   **`X_MIN`, `X_MAX`, `Y_MIN`, `Y_MAX`, `T_MIN`, `T_MAX`** : Domaine spatial et temporel pour la génération de données.
-   **`N_PDE_POINTS`, `N_INITIAL_COND_POINTS`, `N_BOUNDARY_POINTS`** : Nombre de points pour les différents termes de perte.
-   **`USE_ADAPTIVE_SAMPLING`** : Active/désactive l'échantillonnage adaptatif pour les points PDE.
-   **`CHECKPOINT_DIR`, `LOG_DIR`, `MODEL_EXPORT_PATH`** : Répertoires pour les checkpoints, les logs et les modèles exportés.
-   **`SAVE_EVERY_N_EPOCHS`** : Fréquence de sauvegarde des checkpoints.
-   **`EARLY_STOPPING_PATIENCE`, `MIN_DELTA`** : Paramètres pour l'arrêt précoce.

Modifiez ce fichier pour ajuster le comportement de l'entraînement et du modèle.

## Extension à d'Autres EDP
Pour résoudre une nouvelle EDP :
1.  Créez une nouvelle classe qui hérite de `PDE` dans `pinn_industrial.py`.
2.  Implémentez la méthode `residual` pour définir l'équation de votre EDP.
3.  Implémentez la méthode `boundary_conditions` pour gérer les conditions aux limites spécifiques à votre EDP.
4.  Ajoutez votre nouvelle classe PDE à la méthode `_get_pde_solver` dans la classe `PINN`.
5.  Mettez à jour `config.py` avec `PDE_TYPE` et `pde_params` appropriés.
6.  Ajoutez une fonction de génération de données (`generate_your_pde_data`) dans `train.py` et intégrez-la dans la fonction `train`.

## Pipeline de Données CFD
Le module `core/data_pipeline.py` fournit une classe `CFDDataset` pour charger et prétraiter les données de simulation CFD. Actuellement, il est configuré pour lire des fichiers CSV avec des colonnes spécifiques (par exemple, `x`, `Ux`).

Pour intégrer des données CFD industrielles :
-   Modifiez la méthode `_load_simulation` dans `CFDDataset` pour prendre en charge vos formats de données (par exemple, VTK, HDF5, NetCDF) et la structure de fichiers.
-   Assurez-vous que les données sont correctement normalisées pour l'entraînement du PINN.

## Déploiement
Le modèle entraîné est sauvegardé dans le répertoire `MODEL_EXPORT_PATH` spécifié dans `config.py`. Pour le déploiement en production, vous pouvez :
-   Exporter le modèle au format ONNX ou TorchScript pour une inférence optimisée.
-   Construire une API REST (par exemple, avec FastAPI) qui charge le modèle et expose une interface de prédiction.

## Tests
Bien que non inclus dans cette version initiale, des tests unitaires sont cruciaux pour un code de qualité industrielle. Il est recommandé d'utiliser `pytest` pour :
-   Vérifier la correction des calculs de gradients.
-   Assurer la stabilité numérique du modèle.
-   Valider la reproductibilité des résultats.
-   Tester les différentes implémentations d'EDP et de conditions aux limites.

## Applications
- `apps/web_dashboard/` – Tableau de bord React/Vite pour interagir avec l'API de prédiction
- `apps/mobile_coach/` – Application mobile compagnon basée sur Expo (React Native)

## Recherche
- `research/papers/` – Brouillon LaTeX d'un article scientifique comparant CFD vs AI
- `research/benchmarks/` – Notebooks Jupyter avec des benchmarks et des visualisations

## Infrastructure
- `infrastructure/supabase/` – Schéma de base de données et fonctions Edge pour l'inférence serverless
- `infrastructure/docker/` – Environnement Docker pour exécuter des simulations OpenFOAM

## Licence
Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Contact
Samba Ba – @sambathedev – samba@physicsai.com

---
*Ce projet fait partie d'une stratégie visant à relier l'IA et les sciences physiques, dans le but d'avoir un impact académique et une application industrielle.*
