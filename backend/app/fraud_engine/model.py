"""
model.py
─────────
PyTorch MLP fraud detection model.
Architecture:  Input(7) → Dense(64, ReLU) → Dense(32, ReLU) → Dense(1, Sigmoid)

Since we don't have real training data, we initialise with deterministic
mock weights that produce reasonable scores given the feature vector.
The model is designed to be swapped out with real trained weights via
load_model(path).
"""
from __future__ import annotations

import os
import logging
from pathlib import Path

import torch
import torch.nn as nn
import numpy as np

logger = logging.getLogger(__name__)

INPUT_SIZE = 7
MODEL_PATH = Path(__file__).parent / "weights" / "fraud_mlp.pt"


class FraudMLP(nn.Module):
    """
    Multi-layer perceptron for fraud probability prediction.
    Output: sigmoid probability in [0, 1].
    """

    def __init__(self, input_size: int = INPUT_SIZE) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(32, 1),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


def _init_mock_weights(model: FraudMLP) -> None:
    """
    Initialize weights to produce sensible outputs.
    High-risk features (revenue_ratio, cycle_flag, cascade_depth)
    get positive weights; low-risk features get smaller weights.
    These approximate what a trained model would learn.
    """
    torch.manual_seed(42)
    with torch.no_grad():
        # Layer 0 (7→64): bias high-risk features
        w = model.network[0].weight
        nn.init.xavier_uniform_(w)
        # Amplify revenue_ratio(0), cascade_depth(4), cycle_flag(6)
        w[:, 0] *= 2.0   # revenue_ratio
        w[:, 3] *= 1.5   # duplicate_flag
        w[:, 4] *= 2.0   # cascade_depth
        w[:, 6] *= 2.5   # cycle_flag

        # Layer 3 (64→32) and Layer 6 (32→1) — standard init
        nn.init.xavier_uniform_(model.network[3].weight)
        nn.init.xavier_uniform_(model.network[6].weight)


# ── Singleton ─────────────────────────────────────────────────────────────────

_model_instance: FraudMLP | None = None


def load_model(path: Path | None = None) -> FraudMLP:
    """
    Load model from disk or create a new one with mock weights.
    Call once at startup; result is cached globally.
    """
    global _model_instance
    if _model_instance is not None:
        return _model_instance

    model = FraudMLP()

    target = path or MODEL_PATH
    if target.exists():
        try:
            state = torch.load(str(target), map_location="cpu", weights_only=True)
            model.load_state_dict(state)
            logger.info("Loaded fraud model weights from %s", target)
        except Exception as exc:
            logger.warning("Failed to load weights (%s) — using mock weights", exc)
            _init_mock_weights(model)
    else:
        logger.info("No weights file at %s — using mock weights", target)
        _init_mock_weights(model)

    model.eval()
    _model_instance = model
    return model


def predict(features: list[float]) -> float:
    """
    Run inference and return fraud probability in [0, 1].
    Thread-safe (model in eval mode, no grad).
    """
    model = load_model()
    x = torch.tensor([features], dtype=torch.float32)
    with torch.no_grad():
        prob = model(x).item()
    return round(prob, 4)
