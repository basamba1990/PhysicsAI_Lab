"""
Model Versioning - Gestion des versions de modèles PINN/PINO
Assure la traçabilité complète et le déploiement reproductible.
"""

import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ModelVersion:
    """Représente une version de modèle avec métadonnées complètes."""
    
    def __init__(
        self,
        model_id: str,
        version: str,
        model_path: str,
        onnx_path: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        training_data_hash: Optional[str] = None
    ):
        self.model_id = model_id
        self.version = version
        self.model_path = model_path
        self.onnx_path = onnx_path
        self.config = config or {}
        self.metrics = metrics or {}
        self.training_data_hash = training_data_hash
        self.created_at = datetime.now().isoformat()
        self.model_hash = self._compute_model_hash()
    
    def _compute_model_hash(self) -> str:
        """Calcule un hash SHA256 du modèle pour l'intégrité."""
        try:
            with open(self.model_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.warning(f"Impossible de calculer le hash du modèle: {e}")
            return ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la version en dictionnaire."""
        return {
            "model_id": self.model_id,
            "version": self.version,
            "model_path": self.model_path,
            "onnx_path": self.onnx_path,
            "config": self.config,
            "metrics": self.metrics,
            "training_data_hash": self.training_data_hash,
            "model_hash": self.model_hash,
            "created_at": self.created_at
        }


class ModelVersionManager:
    """
    Gestionnaire de versions de modèles.
    Assure le suivi, le stockage et le déploiement des modèles PINN/PINO.
    """
    
    def __init__(self, registry_path: str = "./model_registry"):
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.versions: Dict[str, List[ModelVersion]] = {}
        self._load_registry()
        logger.info(f"ModelVersionManager initialisé: {self.registry_path}")
    
    def _load_registry(self):
        """Charge le registre de versions depuis le disque."""
        registry_file = self.registry_path / "registry.json"
        if registry_file.exists():
            try:
                with open(registry_file, 'r') as f:
                    data = json.load(f)
                    for model_id, versions in data.items():
                        self.versions[model_id] = [
                            ModelVersion(
                                model_id=v["model_id"],
                                version=v["version"],
                                model_path=v["model_path"],
                                onnx_path=v.get("onnx_path"),
                                config=v.get("config"),
                                metrics=v.get("metrics"),
                                training_data_hash=v.get("training_data_hash")
                            )
                            for v in versions
                        ]
                logger.info(f"Registre chargé: {len(self.versions)} modèles")
            except Exception as e:
                logger.warning(f"Erreur lors du chargement du registre: {e}")
    
    def register_model(
        self,
        model_id: str,
        version: str,
        model_path: str,
        onnx_path: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
        training_data_hash: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> ModelVersion:
        """
        Enregistre une nouvelle version de modèle.
        
        Args:
            model_id: Identifiant unique du modèle
            version: Numéro de version (ex: v1.0, v1.1)
            model_path: Chemin vers le fichier du modèle
            onnx_path: Chemin vers le fichier ONNX (optionnel)
            config: Configuration du modèle
            metrics: Métriques de performance
            training_data_hash: Hash des données d'entraînement
            tags: Tags pour catégoriser le modèle
            
        Returns:
            L'objet ModelVersion enregistré
        """
        # Vérifier que le modèle existe
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Fichier modèle non trouvé: {model_path}")
        
        # Vérifier que la version n'existe pas déjà
        if model_id in self.versions:
            existing_versions = [v.version for v in self.versions[model_id]]
            if version in existing_versions:
                raise ValueError(f"Version {version} du modèle {model_id} existe déjà")
        
        # Créer l'objet ModelVersion
        model_version = ModelVersion(
            model_id=model_id,
            version=version,
            model_path=model_path,
            onnx_path=onnx_path,
            config=config,
            metrics=metrics,
            training_data_hash=training_data_hash
        )
        
        # Ajouter au registre
        if model_id not in self.versions:
            self.versions[model_id] = []
        
        self.versions[model_id].append(model_version)
        
        # Sauvegarder le registre
        self._save_registry()
        
        logger.info(f"Modèle enregistré: {model_id} v{version}")
        
        return model_version
    
    def get_model_version(self, model_id: str, version: str) -> Optional[ModelVersion]:
        """Récupère une version spécifique d'un modèle."""
        if model_id not in self.versions:
            return None
        
        for v in self.versions[model_id]:
            if v.version == version:
                return v
        
        return None
    
    def get_latest_version(self, model_id: str) -> Optional[ModelVersion]:
        """Récupère la version la plus récente d'un modèle."""
        if model_id not in self.versions or not self.versions[model_id]:
            return None
        
        # Trier par date de création
        sorted_versions = sorted(self.versions[model_id], key=lambda v: v.created_at, reverse=True)
        return sorted_versions[0]
    
    def list_versions(self, model_id: str) -> List[ModelVersion]:
        """Liste toutes les versions d'un modèle."""
        return self.versions.get(model_id, [])
    
    def list_all_models(self) -> List[str]:
        """Liste tous les modèles enregistrés."""
        return list(self.versions.keys())
    
    def delete_version(self, model_id: str, version: str):
        """Supprime une version de modèle."""
        if model_id not in self.versions:
            raise ValueError(f"Modèle non trouvé: {model_id}")
        
        self.versions[model_id] = [
            v for v in self.versions[model_id] if v.version != version
        ]
        
        if not self.versions[model_id]:
            del self.versions[model_id]
        
        self._save_registry()
        logger.info(f"Version supprimée: {model_id} v{version}")
    
    def promote_to_production(self, model_id: str, version: str) -> Dict[str, Any]:
        """
        Promeut une version en production.
        
        Args:
            model_id: Identifiant du modèle
            version: Version à promouvoir
            
        Returns:
            Informations de promotion
        """
        model_version = self.get_model_version(model_id, version)
        if not model_version:
            raise ValueError(f"Version non trouvée: {model_id} v{version}")
        
        promotion_info = {
            "model_id": model_id,
            "version": version,
            "promoted_at": datetime.now().isoformat(),
            "model_hash": model_version.model_hash,
            "metrics": model_version.metrics,
            "onnx_path": model_version.onnx_path
        }
        
        logger.info(f"Modèle promu en production: {model_id} v{version}")
        
        return promotion_info
    
    def get_model_lineage(self, model_id: str) -> Dict[str, Any]:
        """Retourne l'historique complet d'un modèle."""
        if model_id not in self.versions:
            return {"model_id": model_id, "versions": []}
        
        versions = sorted(self.versions[model_id], key=lambda v: v.created_at)
        
        return {
            "model_id": model_id,
            "total_versions": len(versions),
            "versions": [v.to_dict() for v in versions],
            "first_version": versions[0].created_at if versions else None,
            "latest_version": versions[-1].created_at if versions else None
        }
    
    def compare_versions(self, model_id: str, version1: str, version2: str) -> Dict[str, Any]:
        """Compare deux versions d'un modèle."""
        v1 = self.get_model_version(model_id, version1)
        v2 = self.get_model_version(model_id, version2)
        
        if not v1 or not v2:
            raise ValueError("Une ou les deux versions n'existent pas")
        
        return {
            "model_id": model_id,
            "version1": version1,
            "version2": version2,
            "metrics_diff": {
                key: {
                    "v1": v1.metrics.get(key),
                    "v2": v2.metrics.get(key),
                    "improvement": (v2.metrics.get(key, 0) - v1.metrics.get(key, 0)) / (v1.metrics.get(key, 1) + 1e-8)
                }
                for key in set(v1.metrics.keys()) | set(v2.metrics.keys())
            },
            "config_diff": {
                key: {
                    "v1": v1.config.get(key),
                    "v2": v2.config.get(key)
                }
                for key in set(v1.config.keys()) | set(v2.config.keys())
                if v1.config.get(key) != v2.config.get(key)
            }
        }
    
    def _save_registry(self):
        """Sauvegarde le registre sur le disque."""
        registry_file = self.registry_path / "registry.json"
        
        data = {
            model_id: [v.to_dict() for v in versions]
            for model_id, versions in self.versions.items()
        }
        
        with open(registry_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Registre sauvegardé: {registry_file}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du registre."""
        total_versions = sum(len(versions) for versions in self.versions.values())
        
        return {
            "total_models": len(self.versions),
            "total_versions": total_versions,
            "models": list(self.versions.keys()),
            "versions_per_model": {
                model_id: len(versions)
                for model_id, versions in self.versions.items()
            }
        }


if __name__ == "__main__":
    manager = ModelVersionManager()
    
    # Exemple d'utilisation
    print("--- Model Version Manager ---")
    print(f"Statistiques: {manager.get_statistics()}")
