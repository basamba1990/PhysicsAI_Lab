"""
CFD Data Pipeline - Ingestion, prétraitement et préparation des données
Intègre l'échantillonnage adaptatif (DAS²) pour une efficacité optimale.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional, List
import logging
from pathlib import Path
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class CFDDataPipeline:
    """
    Pipeline pour l'ingestion, le prétraitement et la préparation des données CFD
    pour l'entraînement des modèles PINN.
    Supporte la génération synthétique, le chargement depuis fichiers, et l'échantillonnage adaptatif.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            "output_features": ["temperature"],
            "input_features": ["x", "y", "z"],
            "noise_level": 0.01,
            "adaptive_sampling": True,
            "sampling_method": "das2"  # DAS² ou uniform
        }
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "pipeline_version": "v1.0",
            "datasets_processed": 0
        }
        logger.info("CFDDataPipeline initialisé.")

    def generate_synthetic_data(
        self, 
        n_samples: int = 1000, 
        domain_bounds: Dict[str, Tuple[float, float]] = None,
        physics_type: str = "heat_transfer"
    ) -> Dict[str, np.ndarray]:
        """
        Génère des données CFD synthétiques pour simuler un écoulement thermique.
        
        Args:
            n_samples: Nombre de points de données à générer.
            domain_bounds: Limites du domaine pour chaque dimension (x, y, z).
            physics_type: Type de physique ("heat_transfer", "fluid_flow", "mixed")
            
        Returns:
            Dictionnaire contenant les données géométriques et de température.
        """
        if domain_bounds is None:
            domain_bounds = {
                "x": (0.0, 1.0),
                "y": (0.0, 1.0),
                "z": (0.0, 1.0)
            }

        logger.info(f"Génération de {n_samples} échantillons de données synthétiques ({physics_type}).")

        # Génération des coordonnées géométriques
        x = np.random.uniform(domain_bounds["x"][0], domain_bounds["x"][1], n_samples)
        y = np.random.uniform(domain_bounds["y"][0], domain_bounds["y"][1], n_samples)
        z = np.random.uniform(domain_bounds["z"][0], domain_bounds["z"][1], n_samples)
        geometry_data = np.vstack([x, y, z]).T

        # Génération de la température basée sur une fonction physique réaliste
        if physics_type == "heat_transfer":
            # Gradient thermique avec sources de chaleur
            base_temperature = 20.0 + 50.0 * (x + y + z) / 3.0
            # Ajout de sources de chaleur localisées
            heat_sources = 30.0 * np.exp(-((x - 0.5)**2 + (y - 0.5)**2 + (z - 0.5)**2) / 0.1)
            base_temperature += heat_sources
        elif physics_type == "fluid_flow":
            # Champ de vitesse avec vorticité
            base_temperature = 20.0 + 30.0 * (np.sin(2*np.pi*x) * np.cos(2*np.pi*y))
        else:  # mixed
            base_temperature = 20.0 + 40.0 * (x + y + z) / 3.0 + 20.0 * np.sin(2*np.pi*x)
        
        # Ajout de bruit réaliste
        noise = np.random.normal(0, self.config["noise_level"] * base_temperature.std(), n_samples)
        temperature_data = base_temperature + noise

        # Contraintes physiques
        temperature_data = np.clip(temperature_data, 0, 150)

        logger.info(f"Données synthétiques générées: {n_samples} points, T ∈ [{temperature_data.min():.2f}, {temperature_data.max():.2f}]°C")
        
        self.metadata["datasets_processed"] += 1
        
        return {
            "geometry": geometry_data,
            "temperature": temperature_data,
            "physics_type": physics_type
        }

    def load_cfd_output(self, file_path: str) -> Dict[str, np.ndarray]:
        """
        Charge les données à partir d'un fichier de sortie CFD (CSV, JSON, etc).
        
        Args:
            file_path: Chemin vers le fichier de données CFD.
            
        Returns:
            Dictionnaire contenant les données géométriques et de température.
        """
        logger.info(f"Chargement des données CFD depuis: {file_path}")
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            elif file_ext == '.json':
                df = pd.read_json(file_path)
            else:
                raise ValueError(f"Format de fichier non supporté: {file_ext}")
            
            geometry_data = df[self.config["input_features"]].values
            temperature_data = df[self.config["output_features"][0]].values
            
            logger.info(f"Données CFD chargées: {geometry_data.shape[0]} points")
            self.metadata["datasets_processed"] += 1
            
            return {
                "geometry": geometry_data,
                "temperature": temperature_data
            }
        except FileNotFoundError:
            logger.error(f"Fichier CFD non trouvé: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Erreur lors du chargement du fichier CFD: {e}")
            raise

    def preprocess_data(self, raw_data: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Prétraite les données brutes (normalisation, standardisation).
        
        Args:
            raw_data: Dictionnaire de données brutes.
            
        Returns:
            Dictionnaire de données prétraitées.
        """
        logger.info("Prétraitement des données...")
        
        geometry = raw_data["geometry"]
        temperature = raw_data["temperature"]
        
        # Normalisation des géométries
        geometry_mean = geometry.mean(axis=0)
        geometry_std = geometry.std(axis=0)
        geometry_normalized = (geometry - geometry_mean) / (geometry_std + 1e-8)
        
        # Normalisation de la température
        temp_mean = temperature.mean()
        temp_std = temperature.std()
        temperature_normalized = (temperature - temp_mean) / (temp_std + 1e-8)
        
        processed_data = {
            "geometry": geometry_normalized,
            "temperature": temperature_normalized,
            "geometry_stats": {
                "mean": geometry_mean.tolist(),
                "std": geometry_std.tolist()
            },
            "temperature_stats": {
                "mean": float(temp_mean),
                "std": float(temp_std)
            }
        }
        
        logger.info("Données prétraitées avec succès.")
        return processed_data

    def adaptive_sampling(
        self, 
        raw_data: Dict[str, np.ndarray],
        residuals: Optional[np.ndarray] = None,
        n_new_samples: int = 100,
        method: str = "das2"
    ) -> Dict[str, np.ndarray]:
        """
        Applique l'échantillonnage adaptatif (DAS²) pour concentrer les points
        dans les zones de fort résidu.
        
        Args:
            raw_data: Données brutes
            residuals: Résidus du modèle (si None, utilise une distribution uniforme)
            n_new_samples: Nombre de nouveaux points à générer
            method: Méthode d'échantillonnage ("das2" ou "uniform")
            
        Returns:
            Données augmentées avec nouveaux points d'échantillonnage
        """
        logger.info(f"Échantillonnage adaptatif ({method}): génération de {n_new_samples} nouveaux points")
        
        geometry = raw_data["geometry"]
        temperature = raw_data["temperature"]
        
        if method == "das2" and residuals is not None:
            # DAS² : utiliser les résidus comme poids d'importance
            # Normaliser les résidus pour créer une distribution de probabilité
            residuals_normalized = np.abs(residuals)
            residuals_normalized = residuals_normalized / (residuals_normalized.sum() + 1e-8)
            
            # Sélectionner les points avec probabilité proportionnelle aux résidus
            indices = np.random.choice(
                len(geometry), 
                size=n_new_samples, 
                p=residuals_normalized,
                replace=True
            )
            
            # Ajouter du bruit pour générer de nouveaux points autour des zones de fort résidu
            new_geometry = geometry[indices] + np.random.normal(0, 0.01, (n_new_samples, geometry.shape[1]))
            new_temperature = temperature[indices] + np.random.normal(0, 0.01 * temperature.std(), n_new_samples)
        else:
            # Échantillonnage uniforme
            indices = np.random.choice(len(geometry), size=n_new_samples, replace=True)
            new_geometry = geometry[indices] + np.random.normal(0, 0.01, (n_new_samples, geometry.shape[1]))
            new_temperature = temperature[indices] + np.random.normal(0, 0.01 * temperature.std(), n_new_samples)
        
        # Combiner les données originales et les nouveaux points
        augmented_geometry = np.vstack([geometry, new_geometry])
        augmented_temperature = np.concatenate([temperature, new_temperature])
        
        logger.info(f"Données augmentées: {len(augmented_geometry)} points (était {len(geometry)})")
        
        return {
            "geometry": augmented_geometry,
            "temperature": augmented_temperature,
            "n_original": len(geometry),
            "n_added": n_new_samples
        }

    def split_train_val_test(
        self, 
        data: Dict[str, np.ndarray],
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15
    ) -> Dict[str, Dict[str, np.ndarray]]:
        """
        Divise les données en ensembles d'entraînement, validation et test.
        
        Args:
            data: Données à diviser
            train_ratio: Proportion d'entraînement
            val_ratio: Proportion de validation
            test_ratio: Proportion de test
            
        Returns:
            Dictionnaire avec 'train', 'val', 'test'
        """
        logger.info(f"Division des données: train={train_ratio}, val={val_ratio}, test={test_ratio}")
        
        n_samples = len(data["geometry"])
        indices = np.random.permutation(n_samples)
        
        n_train = int(n_samples * train_ratio)
        n_val = int(n_samples * val_ratio)
        
        train_idx = indices[:n_train]
        val_idx = indices[n_train:n_train + n_val]
        test_idx = indices[n_train + n_val:]
        
        return {
            "train": {
                "geometry": data["geometry"][train_idx],
                "temperature": data["temperature"][train_idx]
            },
            "val": {
                "geometry": data["geometry"][val_idx],
                "temperature": data["temperature"][val_idx]
            },
            "test": {
                "geometry": data["geometry"][test_idx],
                "temperature": data["temperature"][test_idx]
            }
        }

    def get_statistics(self, data: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Calcule les statistiques des données."""
        geometry = data["geometry"]
        temperature = data["temperature"]
        
        return {
            "n_samples": len(geometry),
            "geometry_shape": geometry.shape,
            "temperature_range": [float(temperature.min()), float(temperature.max())],
            "temperature_mean": float(temperature.mean()),
            "temperature_std": float(temperature.std()),
            "geometry_stats": {
                "mean": geometry.mean(axis=0).tolist(),
                "std": geometry.std(axis=0).tolist(),
                "min": geometry.min(axis=0).tolist(),
                "max": geometry.max(axis=0).tolist()
            }
        }

    def save_dataset(self, data: Dict[str, np.ndarray], output_path: str) -> str:
        """Sauvegarde les données en format NPZ avec métadonnées."""
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Sauvegarde des données
        np.savez_compressed(
            output_path,
            geometry=data["geometry"],
            temperature=data["temperature"]
        )
        
        # Sauvegarde des métadonnées
        metadata_path = str(Path(output_path).with_suffix('.json'))
        metadata = {
            "created_at": datetime.now().isoformat(),
            "statistics": self.get_statistics(data),
            "config": self.config,
            "pipeline_metadata": self.metadata
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Dataset sauvegardé: {output_path}")
        return output_path

    def load_dataset(self, input_path: str) -> Dict[str, np.ndarray]:
        """Charge les données depuis un fichier NPZ."""
        data = np.load(input_path)
        return {
            "geometry": data["geometry"],
            "temperature": data["temperature"]
        }


if __name__ == "__main__":
    pipeline = CFDDataPipeline()

    # 1. Génération de données synthétiques
    synthetic_data = pipeline.generate_synthetic_data(n_samples=5000, physics_type="heat_transfer")
    print("\n--- Données Synthétiques Générées ---")
    print(f"Géométrie (shape): {synthetic_data['geometry'].shape}")
    print(f"Température (shape): {synthetic_data['temperature'].shape}")
    print(f"Statistiques: {pipeline.get_statistics(synthetic_data)}")

    # 2. Prétraitement
    processed_data = pipeline.preprocess_data(synthetic_data)
    print("\n--- Données Prétraitées ---")
    print(f"Géométrie prétraitée (moyenne): {processed_data['geometry'].mean(axis=0)}")
    print(f"Température prétraitée (moyenne): {processed_data['temperature'].mean()}")

    # 3. Split train/val/test
    splits = pipeline.split_train_val_test(synthetic_data)
    print("\n--- Split Train/Val/Test ---")
    for split_name, split_data in splits.items():
        print(f"{split_name}: {len(split_data['geometry'])} points")

    # 4. Échantillonnage adaptatif
    residuals = np.random.exponential(1, len(synthetic_data["geometry"]))
    augmented_data = pipeline.adaptive_sampling(synthetic_data, residuals, n_new_samples=500, method="das2")
    print("\n--- Données Augmentées (DAS²) ---")
    print(f"Points originaux: {augmented_data['n_original']}")
    print(f"Points ajoutés: {augmented_data['n_added']}")
    print(f"Total: {len(augmented_data['geometry'])}")
