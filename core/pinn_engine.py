"""
PINN Engine - Physics-Informed Neural Networks avec quantification d'incertitude
Aligné sur les concepts DAS², PINO-PC et B-DeepONet pour une inférence industrielle.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import List, Dict, Any, Tuple, Optional
import logging
import json
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class PhysicsInformedNN(nn.Module):
    """Réseau de neurones informé par la physique avec Dropout pour UQ."""
    
    def __init__(
        self, 
        input_dim: int = 3, 
        hidden_layers: List[int] = None,
        dropout_rate: float = 0.1,
        activation: str = "relu"
    ):
        super(PhysicsInformedNN, self).__init__()
        
        if hidden_layers is None:
            hidden_layers = [64, 128, 64]
        
        layers = []
        prev_dim = input_dim
        
        # Construction des couches cachées avec Dropout pour Monte Carlo Dropout
        for hidden_dim in hidden_layers:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            
            if activation == "relu":
                layers.append(nn.ReLU())
            elif activation == "tanh":
                layers.append(nn.Tanh())
            elif activation == "gelu":
                layers.append(nn.GELU())
            
            layers.append(nn.BatchNorm1d(hidden_dim))
            layers.append(nn.Dropout(dropout_rate))
            prev_dim = hidden_dim
        
        # Couche de sortie
        layers.append(nn.Linear(prev_dim, 1))
        
        self.model = nn.Sequential(*layers)
        self.dropout_rate = dropout_rate
        
        # Initialisation des poids
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialisation Xavier/Glorot pour une convergence rapide."""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_normal_(module.weight)
                nn.init.constant_(module.bias, 0.0)
    
    def forward(self, x: torch.Tensor, training: bool = False) -> torch.Tensor:
        """Forward pass avec option pour forcer le mode training (pour MCDO)."""
        was_training = self.training
        if training:
            self.train()
        output = self.model(x)
        if not training:
            self.eval() if not was_training else self.train()
        return output
    
    def physics_loss(
        self, 
        x: torch.Tensor, 
        y: torch.Tensor, 
        conductivity: float, 
        density: float, 
        specific_heat: float
    ) -> torch.Tensor:
        """
        Calcul de la perte physique basée sur l'équation de la chaleur:
        ρ * c_p * ∂T/∂t = k * ∇²T + Q
        """
        x.requires_grad_(True)
        
        # Température prédite
        T = self.forward(x)
        
        # Gradient premier
        grad_T = torch.autograd.grad(
            T, x, 
            grad_outputs=torch.ones_like(T),
            create_graph=True,
            retain_graph=True
        )[0]
        
        # Laplacien (divergence du gradient)
        laplacian_T = torch.zeros_like(T)
        for i in range(x.shape[1]):
            grad_T_i = torch.autograd.grad(
                grad_T[:, i], x,
                grad_outputs=torch.ones_like(grad_T[:, i]),
                create_graph=True,
                retain_graph=True
            )[0][:, i]
            laplacian_T += grad_T_i
        
        # Équation de la chaleur résiduelle
        heat_eq_residual = density * specific_heat * grad_T[:, 0] - conductivity * laplacian_T
        
        # Perte MSE sur l'équation physique
        physics_loss = torch.mean(heat_eq_residual**2)
        
        return physics_loss


class PINNSurrogate:
    """
    Modèle de substitution Physics-Informed Neural Network.
    Contraint par les équations de transfert thermique.
    Supporte l'export ONNX et la quantification d'incertitude.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Architecture du réseau
        hidden_layers = config.get("hidden_layers", [64, 128, 64])
        dropout_rate = config.get("dropout_rate", 0.1)
        activation = config.get("activation", "relu")
        
        self.model = PhysicsInformedNN(
            input_dim=3, 
            hidden_layers=hidden_layers,
            dropout_rate=dropout_rate,
            activation=activation
        ).to(self.device)
        
        # Optimiseur
        self.learning_rate = config.get("learning_rate", 1e-3)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        
        # Métriques
        self.fidelity_score = 0.0
        self.training_history = []
        self.validation_loss = float('inf')
        self.model_version = config.get("model_version", "v1.0")
        self.created_at = datetime.now().isoformat()
        
        # Paramètres physiques par défaut
        self.conductivity = config.get("conductivity", 200.0)
        self.density = config.get("density", 2700.0)
        self.specific_heat = config.get("specific_heat", 900.0)
        
        logger.info(f"PINN initialisé sur {self.device} - Version: {self.model_version}")
    
    def predict(self, geometry_data: np.ndarray, uncertainty_quantification: bool = False, n_samples: int = 100) -> Dict[str, np.ndarray]:
        """
        Inférence rapide du champ de température avec option UQ.
        
        Args:
            geometry_data: Données géométriques [n_points, 3]
            uncertainty_quantification: Si True, utilise Monte Carlo Dropout
            n_samples: Nombre d'échantillons pour MCDO
            
        Returns:
            Dict avec 'mean' et optionnellement 'std'
        """
        self.model.eval()
        
        with torch.no_grad():
            x_tensor = torch.FloatTensor(geometry_data).to(self.device)
            
            if uncertainty_quantification:
                # Monte Carlo Dropout
                predictions = []
                for _ in range(n_samples):
                    pred = self.model(x_tensor, training=True)
                    predictions.append(pred.cpu().numpy())
                
                predictions = np.array(predictions)
                mean_pred = predictions.mean(axis=0).flatten()
                std_pred = predictions.std(axis=0).flatten()
                
                return {
                    'mean': mean_pred,
                    'std': std_pred,
                    'samples': predictions
                }
            else:
                predictions = self.model(x_tensor)
                predictions = self._apply_physical_constraints(predictions)
                return {'mean': predictions.cpu().numpy().flatten()}
    
    def train(
        self, 
        training_data: Dict[str, np.ndarray], 
        validation_data: Dict[str, np.ndarray],
        epochs: int = 100,
        batch_size: int = 32,
        physics_weight: float = 0.1
    ) -> Dict[str, List[float]]:
        """
        Entraînement du modèle PINN.
        
        Args:
            training_data: {'geometry': X_train, 'temperature': y_train}
            validation_data: {'geometry': X_val, 'temperature': y_val}
            epochs: Nombre d'époques
            batch_size: Taille des batches
            physics_weight: Poids de la perte physique
            
        Returns:
            Historique d'entraînement
        """
        self.model.train()
        
        X_train = torch.FloatTensor(training_data['geometry']).to(self.device)
        y_train = torch.FloatTensor(training_data['temperature']).to(self.device)
        
        X_val = torch.FloatTensor(validation_data['geometry']).to(self.device)
        y_val = torch.FloatTensor(validation_data['temperature']).to(self.device)
        
        history = {
            'train_loss': [],
            'val_loss': [],
            'physics_loss': [],
            'data_loss': []
        }
        
        n_samples = X_train.shape[0]
        n_batches = (n_samples + batch_size - 1) // batch_size
        
        for epoch in range(epochs):
            epoch_train_loss = 0.0
            epoch_physics_loss = 0.0
            epoch_data_loss = 0.0
            
            indices = torch.randperm(n_samples)
            
            for batch_idx in range(n_batches):
                start_idx = batch_idx * batch_size
                end_idx = min((batch_idx + 1) * batch_size, n_samples)
                batch_indices = indices[start_idx:end_idx]
                
                X_batch = X_train[batch_indices]
                y_batch = y_train[batch_indices].unsqueeze(1)
                
                self.optimizer.zero_grad()
                
                y_pred = self.model(X_batch)
                
                # Perte sur les données
                data_loss = nn.functional.mse_loss(y_pred, y_batch)
                
                # Perte physique
                physics_loss = self.model.physics_loss(
                    X_batch, y_pred,
                    self.conductivity, self.density, self.specific_heat
                )
                
                # Perte totale (pondérée)
                total_loss = data_loss + physics_weight * physics_loss
                
                total_loss.backward()
                self.optimizer.step()
                
                epoch_train_loss += total_loss.item()
                epoch_physics_loss += physics_loss.item()
                epoch_data_loss += data_loss.item()
            
            epoch_train_loss /= n_batches
            epoch_physics_loss /= n_batches
            epoch_data_loss /= n_batches
            
            val_loss = self._validate(X_val, y_val)
            
            history['train_loss'].append(epoch_train_loss)
            history['val_loss'].append(val_loss)
            history['physics_loss'].append(epoch_physics_loss)
            history['data_loss'].append(epoch_data_loss)
            
            self.fidelity_score = 1.0 / (1.0 + val_loss)
            
            if epoch % 10 == 0:
                logger.info(
                    f"Epoch {epoch}/{epochs} | "
                    f"Train Loss: {epoch_train_loss:.4e} | "
                    f"Val Loss: {val_loss:.4e} | "
                    f"Fidelity: {self.fidelity_score:.4f}"
                )
        
        self.training_history = history
        self.validation_loss = val_loss
        
        return history
    
    def _validate(self, X_val: torch.Tensor, y_val: torch.Tensor) -> float:
        """Validation du modèle."""
        self.model.eval()
        with torch.no_grad():
            y_pred = self.model(X_val)
            loss = nn.functional.mse_loss(y_pred, y_val.unsqueeze(1))
        self.model.train()
        return loss.item()
    
    def _apply_physical_constraints(self, predictions: torch.Tensor) -> torch.Tensor:
        """Application de contraintes physiques aux prédictions."""
        # Contrainte de positivité (température en Kelvin)
        predictions = torch.clamp(predictions, min=0.0)
        
        # Contrainte de continuité (filtre passe-bas)
        if predictions.shape[0] > 1:
            predictions = 0.5 * predictions + 0.5 * predictions.roll(1, 0)
        
        return predictions
    
    def export_onnx(self, output_path: str, input_shape: Tuple[int, ...] = (1, 3)) -> str:
        """
        Exporte le modèle au format ONNX pour déploiement edge.
        
        Args:
            output_path: Chemin de sortie du fichier ONNX
            input_shape: Shape de l'input pour le modèle ONNX
            
        Returns:
            Chemin du fichier exporté
        """
        self.model.eval()
        
        # Dummy input
        dummy_input = torch.randn(input_shape).to(self.device)
        
        # Export ONNX
        torch.onnx.export(
            self.model,
            dummy_input,
            output_path,
            input_names=['input'],
            output_names=['output'],
            dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}},
            opset_version=14,
            verbose=False
        )
        
        logger.info(f"Modèle exporté en ONNX: {output_path}")
        return output_path
    
    def save_model(self, path: str) -> str:
        """Sauvegarde du modèle avec métadonnées."""
        output_dir = Path(path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'config': self.config,
            'fidelity_score': self.fidelity_score,
            'training_history': self.training_history,
            'model_version': self.model_version,
            'created_at': self.created_at,
            'validation_loss': self.validation_loss
        }
        
        torch.save(checkpoint, path)
        logger.info(f"Modèle sauvegardé: {path}")
        
        # Sauvegarde des métadonnées en JSON
        metadata_path = str(Path(path).with_suffix('.json'))
        with open(metadata_path, 'w') as f:
            json.dump({
                'model_version': self.model_version,
                'created_at': self.created_at,
                'fidelity_score': float(self.fidelity_score),
                'validation_loss': float(self.validation_loss),
                'config': self.config
            }, f, indent=2)
        
        return path
    
    def load_model(self, path: str):
        """Chargement du modèle."""
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.fidelity_score = checkpoint['fidelity_score']
        self.training_history = checkpoint['training_history']
        self.model_version = checkpoint.get('model_version', 'unknown')
        self.created_at = checkpoint.get('created_at', datetime.now().isoformat())
        self.validation_loss = checkpoint.get('validation_loss', float('inf'))
        
        logger.info(f"Modèle chargé: {path} (v{self.model_version})")
    
    def get_model_summary(self) -> Dict[str, Any]:
        """Résumé du modèle."""
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        
        return {
            'total_parameters': total_params,
            'trainable_parameters': trainable_params,
            'fidelity_score': float(self.fidelity_score),
            'validation_loss': float(self.validation_loss),
            'learning_rate': self.learning_rate,
            'device': str(self.device),
            'model_version': self.model_version,
            'created_at': self.created_at
        }


if __name__ == "__main__":
    # Configuration
    config = {
        "hidden_layers": [64, 128, 64],
        "learning_rate": 1e-3,
        "batch_size": 32,
        "dropout_rate": 0.1,
        "model_version": "v1.0"
    }
    
    # Initialisation du modèle
    pinn = PINNSurrogate(config)
    
    # Génération de données synthétiques
    n_samples = 1000
    geometry = np.random.randn(n_samples, 3)
    temperature = np.random.uniform(20, 100, n_samples)
    
    # Split train/validation
    split_idx = int(0.8 * n_samples)
    train_data = {
        'geometry': geometry[:split_idx],
        'temperature': temperature[:split_idx]
    }
    val_data = {
        'geometry': geometry[split_idx:],
        'temperature': temperature[split_idx:]
    }
    
    # Entraînement
    history = pinn.train(train_data, val_data, epochs=50)
    
    # Prédiction avec UQ
    test_geometry = np.random.randn(10, 3)
    predictions = pinn.predict(test_geometry, uncertainty_quantification=True, n_samples=100)
    
    print(f"Score de fidélité: {pinn.fidelity_score:.4f}")
    print(f"Résumé du modèle: {pinn.get_model_summary()}")
    print(f"Prédictions moyennes: {predictions['mean'][:5]}")
    print(f"Incertitudes: {predictions['std'][:5]}")
    
    # Export ONNX
    pinn.export_onnx("/tmp/pinn_model.onnx")
