"""
Physics AI Dashboard - Core Module
Contient les moteurs PINN/PINO, pipelines de données, validation éthique et gestion des versions.
"""

from .pinn_engine import PhysicsInformedNN, PINNSurrogate
from .data_pipeline import CFDDataPipeline
from .ethics_validator import EthicsValidator
from .model_versioning import ModelVersion, ModelVersionManager

__version__ = "1.0.0"
__all__ = [
    "PhysicsInformedNN",
    "PINNSurrogate",
    "CFDDataPipeline",
    "EthicsValidator",
    "ModelVersion",
    "ModelVersionManager"
]
