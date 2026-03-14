# Physics-Informed Neural Network for Burgers' equation
import torch
import torch.nn as nn
import numpy as np

class PINN(nn.Module):
    def __init__(self, layers=[2, 50, 50, 50, 1]):
        super().__init__()
        self.activation = nn.Tanh()
        self.layers = nn.ModuleList()
        for i in range(len(layers)-1):
            self.layers.append(nn.Linear(layers[i], layers[i+1]))
            nn.init.xavier_uniform_(self.layers[-1].weight)

    def forward(self, x, t):
        # Concatenate inputs
        u = torch.cat([x, t], dim=1)
        for layer in self.layers[:-1]:
            u = self.activation(layer(u))
        u = self.layers[-1](u)
        return u

    def loss(self, x, t, u_exact=None, nu=0.01):
        x.requires_grad_(True)
        t.requires_grad_(True)
        u = self.forward(x, t)

        # Compute derivatives
        u_t = torch.autograd.grad(u, t, grad_outputs=torch.ones_like(u), create_graph=True)[0]
        u_x = torch.autograd.grad(u, x, grad_outputs=torch.ones_like(u), create_graph=True)[0]
        u_xx = torch.autograd.grad(u_x, x, grad_outputs=torch.ones_like(u_x), create_graph=True)[0]

        # Burgers' equation residual
        f = u_t + u * u_x - nu * u_xx

        # Data loss (if exact solution provided)
        mse_u = torch.mean((u - u_exact)**2) if u_exact is not None else torch.tensor(0.0)
        mse_f = torch.mean(f**2)

        return mse_u + mse_f

    def predict(self, x, t):
        self.eval()
        with torch.no_grad():
            return self.forward(x, t)
