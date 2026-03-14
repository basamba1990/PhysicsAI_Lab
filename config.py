
import os
import torch

class Config:
    # General settings
    PROJECT_NAME = "PINN_Industrial_MultiPDE"
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    
    # --- SELECT THE PDE TO RUN ---
    # Options: \'burgers\', \'navier_stokes_2d\', \'heat_equation_2d\', \'pino_placeholder\'
    PDE_TYPE = "heat_equation_2d"

    # =========================================================================
    # TRAINING SETTINGS (can be fine-tuned per PDE)
    # =========================================================================
    EPOCHS = 75000
    LEARNING_RATE = 1e-4
    BATCH_SIZE = 2048
    
    # =========================================================================
    # MODEL ARCHITECTURE
    # =========================================================================
    # Note: Adjust layers based on the selected PDE_TYPE
    # Burgers (1D+t): input=2 (x,t), output=1 (u)
    # Navier-Stokes (2D steady): input=2 (x,y), output=3 (u,v,p)
    # Heat Equation (2D+t): input=3 (x,y,t), output=1 (T)
    LAYERS = {
        \'burgers\': [2, 50, 50, 50, 1],
        \'navier_stokes_2d\': [2, 64, 64, 64, 64, 3],
        \'heat_equation_2d\': [3, 64, 128, 128, 64, 1],
        \'pino_placeholder\': [2, 128, 128, 128, 1] # Example layers for a PINO, adjust as needed
    }
    ACTIVATION = "tanh"
    USE_BATCH_NORM = True
    USE_DROPOUT = True # Enable/disable dropout for UQ
    DROPOUT_RATE = 0.1
    
    # =========================================================================
    # PDE-SPECIFIC PARAMETERS
    # =========================================================================
    # Burgers\' Equation
    BURGERS_NU = 0.01

    # Navier-Stokes 2D
    NAVIER_STOKES_NU = 0.01 / torch.pi
    NAVIER_STOKES_RHO = 1.0

    # Heat Equation 2D
    HEAT_CONDUCTIVITY = 1.0
    HEAT_DENSITY = 1.0
    HEAT_SPECIFIC_HEAT = 1.0

    # =========================================================================
    # DATA GENERATION SETTINGS
    # =========================================================================
    # Domain boundaries
    X_MIN = 0.0
    X_MAX = 1.0
    Y_MIN = 0.0
    Y_MAX = 1.0
    T_MIN = 0.0
    T_MAX = 1.0
    
    # Number of points for training
    N_PDE_POINTS = 25000
    N_INITIAL_COND_POINTS = 1000 # For time-dependent problems
    N_BOUNDARY_POINTS = 1000     # Per boundary segment

    # Adaptive Sampling
    USE_ADAPTIVE_SAMPLING = True # Enable/disable adaptive sampling
    
    # =========================================================================
    # CHECKPOINTING, LOGGING, AND EARLY STOPPING
    # =========================================================================
    CHECKPOINT_DIR = "./checkpoints"
    LOG_DIR = "./logs"
    MODEL_EXPORT_PATH = "./exported_models"
    SAVE_EVERY_N_EPOCHS = 5000
    
    EARLY_STOPPING_PATIENCE = 15000
    MIN_DELTA = 1e-8
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    @staticmethod
    def get_layers():
        return Config.LAYERS[Config.PDE_TYPE]

    @staticmethod
    def get_pde_params():
        if Config.PDE_TYPE == \'burgers\':
            return {\'nu\': Config.BURGERS_NU}
        elif Config.PDE_TYPE == \'navier_stokes_2d\':
            return {\'nu\': Config.NAVIER_STOKES_NU, \'rho\': Config.NAVIER_STOKES_RHO}
        elif Config.PDE_TYPE == \'heat_equation_2d\':
            return {\'conductivity\': Config.HEAT_CONDUCTIVITY, \'density\': Config.HEAT_DENSITY, \'specific_heat\': Config.HEAT_SPECIFIC_HEAT}
        elif Config.PDE_TYPE == \'pino_placeholder\':
            return {} # PINO might have different params
        return {}

    @staticmethod
    def setup_directories():
        os.makedirs(Config.CHECKPOINT_DIR, exist_ok=True)
        os.makedirs(Config.LOG_DIR, exist_ok=True)
        os.makedirs(Config.MODEL_EXPORT_PATH, exist_ok=True)

# Setup directories on import
Config.setup_directories()
