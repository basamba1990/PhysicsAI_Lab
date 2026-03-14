
import numpy as np
import pandas as pd
from pathlib import Path
import torch
from torch.utils.data import Dataset, DataLoader
import logging

logger = logging.getLogger(__name__)

class CFDDataset(Dataset):
    """A PyTorch Dataset for CFD simulation data."""
    def __init__(self, data_dir, case_name, normalize=True):
        self.data_dir = Path(data_dir)
        self.case_name = case_name
        self.normalize = normalize
        self.x, self.u = self._load_simulation()
        self.x_mean, self.x_std, self.u_mean, self.u_std = None, None, None, None

        if self.normalize:
            self.x, self.u, (self.x_mean, self.x_std, self.u_mean, self.u_std) = self._normalize(self.x, self.u)
        
        logger.info(f"Loaded CFD data for case '{case_name}' with {len(self.x)} points.")

    def _load_simulation(self):
        # Assumes OpenFOAM postProcessing/sets/ or similar CSV
        # This is a placeholder; in a real industrial setting, this would be more robust
        # and handle various CFD output formats (e.g., VTK, HDF5, NetCDF).
        file_path = self.data_dir / self.case_name / "U.csv"
        if not file_path.exists():
            logger.error(f"Simulation data not found at {file_path}")
            raise FileNotFoundError(f"Simulation data not found at {file_path}")
        
        try:
            df = pd.read_csv(file_path)
            # Expected columns: x, y, z, Ux, Uy, Uz, p (adjust as needed)
            # For 1D Burgers, we might only need x and Ux
            if all(col in df.columns for col in ["x", "Ux"]):
                x = df[["x"]].values.astype(np.float32)
                u = df[["Ux"]].values.astype(np.float32)
            elif all(col in df.columns for col in ["x", "y", "Ux", "Uy"]): # For 2D cases
                x = df[["x", "y"]].values.astype(np.float32)
                u = df[["Ux", "Uy"]].values.astype(np.float32)
            else:
                raise ValueError("CSV file does not contain expected columns for CFD data (e.g., x, Ux or x, y, Ux, Uy).")
            
            return torch.tensor(x), torch.tensor(u)
        except Exception as e:
            logger.error(f"Error loading CFD data from {file_path}: {e}")
            raise

    def _normalize(self, x, u):
        x_mean, x_std = x.mean(axis=0), x.std(axis=0)
        u_mean, u_std = u.mean(axis=0), u.std(axis=0)
        x_norm = (x - x_mean) / (x_std + 1e-8)
        u_norm = (u - u_mean) / (u_std + 1e-8)
        return x_norm, u_norm, (x_mean, x_std, u_mean, u_std)

    def __len__(self):
        return len(self.x)

    def __getitem__(self, idx):
        return {"x": self.x[idx], "u": self.u[idx]}

    def get_normalization_params(self):
        return self.x_mean, self.x_std, self.u_mean, self.u_std


# Example usage (can be integrated into train.py or a separate data preparation script)
if __name__ == "__main__":
    # Create dummy data for demonstration
    dummy_data_dir = Path("./data/cfd_simulations/dummy_case")
    dummy_data_dir.mkdir(parents=True, exist_ok=True)
    dummy_df = pd.DataFrame({
        "x": np.linspace(-1, 1, 100),
        "Ux": np.sin(np.linspace(-1, 1, 100) * np.pi)
    })
    dummy_df.to_csv(dummy_data_dir / "U.csv", index=False)

    try:
        cfd_dataset = CFDDataset(data_dir="./data/cfd_simulations", case_name="dummy_case", normalize=True)
        cfd_dataloader = DataLoader(cfd_dataset, batch_size=10, shuffle=True)

        for i, batch in enumerate(cfd_dataloader):
            print(f"Batch {i}: x_shape={batch["x"].shape}, u_shape={batch["u"].shape}")
            if i == 0: # Print first batch
                print(batch)
                break

        x_mean, x_std, u_mean, u_std = cfd_dataset.get_normalization_params()
        print(f"Normalization params: x_mean={x_mean}, x_std={x_std}, u_mean={u_mean}, u_std={u_std}")

    except FileNotFoundError as e:
        logger.error(f"Error: {e}. Please ensure dummy data is created or provide a valid path.")
    except ValueError as e:
        logger.error(f"Error: {e}")


