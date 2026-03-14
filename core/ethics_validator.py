# Simple fairness / bias checker for simulation outcomes
import numpy as np

class EthicsValidator:
    def __init__(self, sensitive_features=None):
        self.sensitive_features = sensitive_features or []

    def check_bias(self, predictions, ground_truth, group_ids):
        """
        predictions: array of model outputs
        ground_truth: array of true values
        group_ids: array of group labels (e.g., 0/1 for two groups)
        """
        errors = np.abs(predictions - ground_truth)
        groups = np.unique(group_ids)
        if len(groups) != 2:
            return {"warning": "Need exactly two groups for disparity check"}

        group0_err = errors[group_ids == groups[0]].mean()
        group1_err = errors[group_ids == groups[1]].mean()
        disparity = abs(group0_err - group1_err)

        return {
            "mean_error_group0": float(group0_err),
            "mean_error_group1": float(group1_err),
            "disparity": float(disparity),
            "threshold_exceeded": bool(disparity > 0.05)  # example threshold
        }
