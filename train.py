
import torch
import numpy as np
import logging
import os
import time
from datetime import datetime
from torch.utils.data import DataLoader

from core.pinn_industrial import PINN, BurgersEquation, NavierStokes2D, HeatEquation2D, PINO
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class EarlyStopping:
    """Early stops the training if validation loss doesn't improve after a given patience."""
    def __init__(self, patience=7, verbose=False, delta=0, path=\'checkpoint.pt\', trace_func=logger.info):
        self.patience = patience
        self.verbose = verbose
        self.counter = 0
        self.best_score = None
        self.early_stop = False
        self.val_loss_min = np.Inf
        self.delta = delta
        self.path = path
        self.trace_func = trace_func

    def __call__(self, val_loss, model):
        score = -val_loss

        if self.best_score is None:
            self.best_score = score
            self.save_checkpoint(val_loss, model)
        elif score < self.best_score + self.delta:
            self.counter += 1
            self.trace_func(f\"EarlyStopping counter: {self.counter} out of {self.patience}\")
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_score = score
            self.save_checkpoint(val_loss, model)
            self.counter = 0

    def save_checkpoint(self, val_loss, model):
        """Saves model when validation loss decrease."""
        if self.verbose:
            self.trace_func(f\"Validation loss decreased ({self.val_loss_min:.6f} --> {val_loss:.6f}).  Saving model ...\")
        torch.save(model.state_dict(), self.path)
        self.val_loss_min = val_loss

def generate_burgers_data(config):
    """Generates collocation points, initial conditions, and boundary conditions for Burgers equation."""
    # Collocation points (PDE points)
    x_pde = torch.linspace(config.X_MIN, config.X_MAX, int(np.sqrt(config.N_PDE_POINTS)), device=config.DEVICE)
    t_pde = torch.linspace(config.T_MIN, config.T_MAX, int(np.sqrt(config.N_PDE_POINTS)), device=config.DEVICE)
    x_pde_mesh, t_pde_mesh = torch.meshgrid(x_pde, t_pde, indexing=\'ij\')
    x_pde = x_pde_mesh.reshape(-1, 1)
    t_pde = t_pde_mesh.reshape(-1, 1)

    # Initial conditions (t=0)
    x_ic = torch.linspace(config.X_MIN, config.X_MAX, config.N_INITIAL_COND_POINTS, device=config.DEVICE).reshape(-1, 1)
    t_ic = torch.full_like(x_ic, config.T_MIN, device=config.DEVICE)
    u_ic = -torch.sin(np.pi * x_ic)

    # Boundary conditions (x=-1 and x=1)
    t_bc = torch.linspace(config.T_MIN, config.T_MAX, config.N_BOUNDARY_POINTS, device=config.DEVICE).reshape(-1, 1)
    x_bc_left = torch.full_like(t_bc, config.X_MIN, device=config.DEVICE)
    u_bc_left = torch.zeros_like(t_bc) # Assuming u(-1, t) = 0
    x_bc_right = torch.full_like(t_bc, config.X_MAX, device=config.DEVICE)
    u_bc_right = torch.zeros_like(t_bc) # Assuming u(1, t) = 0

    boundary_conditions = [
        ((x_bc_left, t_bc), (u_bc_left,)),
        ((x_bc_right, t_bc), (u_bc_right,))
    ]

    return (x_pde, t_pde), ((x_ic, t_ic), (u_ic,)), boundary_conditions

def generate_navier_stokes_2d_data(config):
    """Generates collocation points and boundary conditions for 2D Navier-Stokes equation (e.g., Lid-driven cavity)."""
    # Collocation points (PDE points)
    x_pde = torch.linspace(config.X_MIN, config.X_MAX, int(np.sqrt(config.N_PDE_POINTS)), device=config.DEVICE)
    y_pde = torch.linspace(config.Y_MIN, config.Y_MAX, int(np.sqrt(config.N_PDE_POINTS)), device=config.DEVICE)
    x_pde_mesh, y_pde_mesh = torch.meshgrid(x_pde, y_pde, indexing=\'ij\')
    x_pde = x_pde_mesh.reshape(-1, 1)
    y_pde = y_pde_mesh.reshape(-1, 1)

    # Boundary conditions (Lid-driven cavity example)
    # Bottom wall (y=0): u=0, v=0
    x_bottom = torch.linspace(config.X_MIN, config.X_MAX, config.N_BOUNDARY_POINTS, device=config.DEVICE).reshape(-1, 1)
    y_bottom = torch.full_like(x_bottom, config.Y_MIN, device=config.DEVICE)
    u_bottom = torch.zeros_like(x_bottom)
    v_bottom = torch.zeros_like(x_bottom)

    # Top wall (y=1): u=1, v=0
    x_top = torch.linspace(config.X_MIN, config.X_MAX, config.N_BOUNDARY_POINTS, device=config.DEVICE).reshape(-1, 1)
    y_top = torch.full_like(x_top, config.Y_MAX, device=config.DEVICE)
    u_top = torch.ones_like(x_top)
    v_top = torch.zeros_like(x_top)

    # Left wall (x=0): u=0, v=0
    y_left = torch.linspace(config.Y_MIN, config.Y_MAX, config.N_BOUNDARY_POINTS, device=config.DEVICE).reshape(-1, 1)
    x_left = torch.full_like(y_left, config.X_MIN, device=config.DEVICE)
    u_left = torch.zeros_like(y_left)
    v_left = torch.zeros_like(y_left)

    # Right wall (x=1): u=0, v=0
    y_right = torch.linspace(config.Y_MIN, config.Y_MAX, config.N_BOUNDARY_POINTS, device=config.DEVICE).reshape(-1, 1)
    x_right = torch.full_like(y_right, config.X_MAX, device=config.DEVICE)
    u_right = torch.zeros_like(y_right)
    v_right = torch.zeros_like(y_right)

    boundary_conditions = [
        ((x_bottom, y_bottom), (u_bottom, v_bottom, None)), # None for pressure if not specified
        ((x_top, y_top), (u_top, v_top, None)),
        ((x_left, y_left), (u_left, v_left, None)),
        ((x_right, y_right), (u_right, v_right, None))
    ]

    return (x_pde, y_pde), None, boundary_conditions

def generate_heat_equation_2d_data(config):
    """Generates collocation points, initial conditions, and boundary conditions for 2D Heat Equation."""
    # Collocation points (PDE points)
    x_pde = torch.linspace(config.X_MIN, config.X_MAX, int(config.N_PDE_POINTS**(1/3)), device=config.DEVICE)
    y_pde = torch.linspace(config.Y_MIN, config.Y_MAX, int(config.N_PDE_POINTS**(1/3)), device=config.DEVICE)
    t_pde = torch.linspace(config.T_MIN, config.T_MAX, int(config.N_PDE_POINTS**(1/3)), device=config.DEVICE)
    x_pde_mesh, y_pde_mesh, t_pde_mesh = torch.meshgrid(x_pde, y_pde, t_pde, indexing=\'ij\')
    x_pde = x_pde_mesh.reshape(-1, 1)
    y_pde = y_pde_mesh.reshape(-1, 1)
    t_pde = t_pde_mesh.reshape(-1, 1)

    # Initial conditions (t=0)
    x_ic = torch.linspace(config.X_MIN, config.X_MAX, int(np.sqrt(config.N_INITIAL_COND_POINTS)), device=config.DEVICE)
    y_ic = torch.linspace(config.Y_MIN, config.Y_MAX, int(np.sqrt(config.N_INITIAL_COND_POINTS)), device=config.DEVICE)
    x_ic_mesh, y_ic_mesh = torch.meshgrid(x_ic, y_ic, indexing=\'ij\')
    x_ic = x_ic_mesh.reshape(-1, 1)
    y_ic = y_ic_mesh.reshape(-1, 1)
    t_ic = torch.full_like(x_ic, config.T_MIN, device=config.DEVICE)
    # Example initial condition: T(x,y,0) = sin(pi*x) * sin(pi*y)
    u_ic = torch.sin(np.pi * x_ic) * torch.sin(np.pi * y_ic)

    # Boundary conditions (Dirichlet, e.g., T=0 on all boundaries)
    boundary_conditions = []

    # Bottom wall (y=0)
    x_bc_bottom = torch.linspace(config.X_MIN, config.X_MAX, config.N_BOUNDARY_POINTS, device=config.DEVICE).reshape(-1, 1)
    t_bc_bottom = torch.linspace(config.T_MIN, config.T_MAX, config.N_BOUNDARY_POINTS, device=config.DEVICE).reshape(-1, 1)
    x_bc_bottom_mesh, t_bc_bottom_mesh = torch.meshgrid(x_bc_bottom, t_bc_bottom, indexing=\'ij\')
    x_bc_bottom = x_bc_bottom_mesh.reshape(-1, 1)
    y_bc_bottom = torch.full_like(x_bc_bottom, config.Y_MIN, device=config.DEVICE)
    t_bc_bottom = t_bc_bottom_mesh.reshape(-1, 1)
    T_bc_bottom = torch.zeros_like(x_bc_bottom)
    boundary_conditions.append(((x_bc_bottom, y_bc_bottom, t_bc_bottom), (T_bc_bottom,)))

    # Top wall (y=1)
    x_bc_top = torch.linspace(config.X_MIN, config.X_MAX, config.N_BOUNDARY_POINTS, device=config.DEVICE).reshape(-1, 1)
    t_bc_top = torch.linspace(config.T_MIN, config.T_MAX, config.N_BOUNDARY_POINTS, device=config.DEVICE).reshape(-1, 1)
    x_bc_top_mesh, t_bc_top_mesh = torch.meshgrid(x_bc_top, t_bc_top, indexing=\'ij\')
    x_bc_top = x_bc_top_mesh.reshape(-1, 1)
    y_bc_top = torch.full_like(x_bc_top, config.Y_MAX, device=config.DEVICE)
    t_bc_top = t_bc_top_mesh.reshape(-1, 1)
    T_bc_top = torch.zeros_like(x_bc_top)
    boundary_conditions.append(((x_bc_top, y_bc_top, t_bc_top), (T_bc_top,)))

    # Left wall (x=0)
    y_bc_left = torch.linspace(config.Y_MIN, config.Y_MAX, config.N_BOUNDARY_POINTS, device=config.DEVICE).reshape(-1, 1)
    t_bc_left = torch.linspace(config.T_MIN, config.T_MAX, config.N_BOUNDARY_POINTS, device=config.DEVICE).reshape(-1, 1)
    y_bc_left_mesh, t_bc_left_mesh = torch.meshgrid(y_bc_left, t_bc_left, indexing=\'ij\')
    y_bc_left = y_bc_left_mesh.reshape(-1, 1)
    x_bc_left = torch.full_like(y_bc_left, config.X_MIN, device=config.DEVICE)
    t_bc_left = t_bc_left_mesh.reshape(-1, 1)
    T_bc_left = torch.zeros_like(y_bc_left)
    boundary_conditions.append(((x_bc_left, y_bc_left, t_bc_left), (T_bc_left,)))

    # Right wall (x=1)
    y_bc_right = torch.linspace(config.Y_MIN, config.Y_MAX, config.N_BOUNDARY_POINTS, device=config.DEVICE).reshape(-1, 1)
    t_bc_right = torch.linspace(config.T_MIN, config.T_MAX, config.N_BOUNDARY_POINTS, device=config.DEVICE).reshape(-1, 1)
    y_bc_right_mesh, t_bc_right_mesh = torch.meshgrid(y_bc_right, t_bc_right, indexing=\'ij\')
    y_bc_right = y_bc_right_mesh.reshape(-1, 1)
    x_bc_right = torch.full_like(y_bc_right, config.X_MAX, device=config.DEVICE)
    t_bc_right = t_bc_right_mesh.reshape(-1, 1)
    T_bc_right = torch.zeros_like(y_bc_right)
    boundary_conditions.append(((x_bc_right, y_bc_right, t_bc_right), (T_bc_right,)))

    return (x_pde, y_pde, t_pde), ((x_ic, y_ic, t_ic), (u_ic,)), boundary_conditions

def train():
    logger.info("Starting PINN training process...")
    config = Config()
    device = torch.device(config.DEVICE)

    # Generate data based on PDE type
    pde_points = None
    data_points = None
    boundary_conditions = None

    if config.PDE_TYPE == \'burgers\':
        pde_points, data_points, boundary_conditions = generate_burgers_data(config)
    elif config.PDE_TYPE == \'navier_stokes_2d\':
        pde_points, data_points, boundary_conditions = generate_navier_stokes_2d_data(config)
    elif config.PDE_TYPE == \'heat_equation_2d\':
        pde_points, data_points, boundary_conditions = generate_heat_equation_2d_data(config)
    elif config.PDE_TYPE == \'pino_placeholder\':
        logger.info("Initializing PINO placeholder. Note: Full PINO implementation and training loop are required.")
        model = PINO(layers=config.get_layers(), device=device).to(device) # Assuming PINO takes similar args
        optimizer = torch.optim.Adam(model.parameters(), lr=config.LEARNING_RATE)
        # PINO training loop would be significantly different, focusing on operator learning
        # For now, we'll just log that it's a placeholder.
        logger.info("PINO placeholder initialized. Skipping detailed training for this placeholder.")
        return model
    else:
        raise ValueError(f"Unsupported PDE type for data generation: {config.PDE_TYPE}")

    # Initialize model
    model = PINN(layers=config.get_layers(), activation=torch.tanh, 
                 pde_type=config.PDE_TYPE, pde_params=config.get_pde_params(), 
                 device=device, use_dropout=config.USE_DROPOUT).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=config.LEARNING_RATE)
    
    # Early stopping setup
    early_stopping = EarlyStopping(patience=config.EARLY_STOPPING_PATIENCE, verbose=True, 
                                   delta=config.MIN_DELTA, path=os.path.join(config.CHECKPOINT_DIR, \'checkpoint.pt\'))

    logger.info(f"Training on device: {device}")
    logger.info(f"Model architecture: {model}")

    start_time = time.time()
    for epoch in range(1, config.EPOCHS + 1):
        model.train()
        optimizer.zero_grad()

        # Adaptive Sampling: Calculate PDE weights based on previous epoch's residuals
        pde_weights = None
        if config.USE_ADAPTIVE_SAMPLING and epoch > 1: # Start adaptive sampling after first epoch
            with torch.no_grad():
                # Compute individual residuals for weighting
                if isinstance(model.pde, BurgersEquation):
                    u_pde, u_t_pde, u_x_pde, u_xx_pde = model.compute_derivatives(*pde_points)
                    f_pde_individual = model.pde.residual(u_pde, u_t_pde, u_x_pde, u_xx_pde)**2
                elif isinstance(model.pde, NavierStokes2D):
                    u_pde, v_pde, p_pde, u_x_pde, u_y_pde, u_xx_pde, u_yy_pde, v_x_pde, v_y_pde, v_xx_pde, v_yy_pde, p_x_pde, p_y_pde = model.compute_derivatives(*pde_points)
                    continuity_eq, x_momentum_eq, y_momentum_eq = model.pde.residual(u_pde, v_pde, p_pde, u_x_pde, u_y_pde, u_xx_pde, u_yy_pde, v_x_pde, v_y_pde, v_xx_pde, v_yy_pde, p_x_pde, p_y_pde)
                    f_pde_individual = continuity_eq**2 + x_momentum_eq**2 + y_momentum_eq**2
                elif isinstance(model.pde, HeatEquation2D):
                    T_pde, T_t_pde, T_x_pde, T_y_pde, T_xx_pde, T_yy_pde = model.compute_derivatives(*pde_points)
                    f_pde_individual = model.pde.residual(T_pde, T_t_pde, T_x_pde, T_y_pde, T_xx_pde, T_yy_pde)**2
                else:
                    f_pde_individual = torch.ones(pde_points[0].shape[0], 1, device=device) # Default to uniform if not implemented
                
                # Simple adaptive weighting: higher residual points get higher weights
                pde_weights = f_pde_individual / f_pde_individual.sum() * f_pde_individual.shape[0]
                pde_weights = pde_weights.detach()

        # Compute loss
        total_loss, mse_f, mse_u, mse_bc = model.loss_function(
            pde_points,
            data_points=data_points,
            boundary_conditions=boundary_conditions,
            pde_weights=pde_weights
        )

        total_loss.backward()
        optimizer.step()

        if epoch % config.SAVE_EVERY_N_EPOCHS == 0 or epoch == 1:
            logger.info(f"Epoch {epoch}/{config.EPOCHS} - Total Loss: {total_loss.item():.6e}, "
                        f"PDE Loss: {mse_f.item():.6e}, Data Loss: {mse_u.item():.6e}, "
                        f"BC Loss: {mse_bc.item():.6e}")
            
            # Save checkpoint
            checkpoint_path = os.path.join(config.CHECKPOINT_DIR, f"model_epoch_{epoch}.pt")
            torch.save(model.state_dict(), checkpoint_path)
            logger.info(f"Model checkpoint saved to {checkpoint_path}")

        # Early stopping check (using total_loss as validation loss for simplicity)
        early_stopping(total_loss.item(), model)
        if early_stopping.early_stop:
            logger.info("Early stopping triggered.")
            break

    end_time = time.time()
    logger.info(f"Training finished in {(end_time - start_time):.2f} seconds.")
    logger.info("Loading best model found by early stopping...")
    model.load_state_dict(torch.load(early_stopping.path))
    logger.info("Training complete.")

    # Save final model
    final_model_path = os.path.join(config.MODEL_EXPORT_PATH, f"final_pinn_{config.PDE_TYPE}_{datetime.now().strftime(\"%Y%m%d_%H%M%S\")}.pt")
    torch.save(model.state_dict(), final_model_path)
    logger.info(f"Final model saved to {final_model_path}")

    # Uncertainty Quantification (UQ) demonstration
    if config.USE_DROPOUT:
        logger.info("Demonstrating Uncertainty Quantification with Monte Carlo Dropout...")
        # For demonstration, let's use a subset of PDE points
        sample_inputs = [p.clone().detach() for p in pde_points]
        mean_predictions, std_predictions = model.predict_with_uncertainty(*sample_inputs, num_samples=100)
        logger.info(f"Mean predictions shape: {mean_predictions.shape}")
        if std_predictions is not None:
            logger.info(f"Standard deviation of predictions shape (Uncertainty): {std_predictions.shape}")
            logger.info(f"Example mean prediction (first 5): {mean_predictions[:5].flatten().tolist()}")
            logger.info(f"Example std prediction (first 5): {std_predictions[:5].flatten().tolist()}")
        else:
            logger.info("UQ was not performed as dropout is not active during inference or num_samples is 0.")

    return model

if __name__ == "__main__":
    train()
