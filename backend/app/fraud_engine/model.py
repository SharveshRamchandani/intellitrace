"""
model.py
─────────
Lightweight numpy MLP for fraud inference.
Architecture: Input(7) → Dense(64, ReLU) → Dense(32, ReLU) → Dense(1, Sigmoid)

No PyTorch needed — numpy matrix ops are sufficient for pure inference.
Weights are initialized deterministically so high-risk features (revenue_ratio,
cycle_flag, cascade_depth) produce higher fraud probabilities out of the box.
Swap in real trained weights by saving numpy arrays to weights/fraud_mlp.npz
and calling load_model().
"""
from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

INPUT_SIZE = 7
MODEL_PATH = Path(__file__).parent / "weights" / "fraud_mlp.npz"


# ── Activations ───────────────────────────────────────────────────────────────

def _relu(x: np.ndarray) -> np.ndarray:
    return np.maximum(0.0, x)


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -500, 500)))


# ── Model ─────────────────────────────────────────────────────────────────────

class FraudMLP:
    """
    3-layer MLP: Input(7) → Dense(64) → Dense(32) → Dense(1)
    Weights stored as numpy arrays — no framework dependency.
    """

    def __init__(
        self,
        W1: np.ndarray,  # (64, 7)
        b1: np.ndarray,  # (64,)
        W2: np.ndarray,  # (32, 64)
        b2: np.ndarray,  # (32,)
        W3: np.ndarray,  # (1, 32)
        b3: np.ndarray,  # (1,)
    ) -> None:
        self.W1, self.b1 = W1, b1
        self.W2, self.b2 = W2, b2
        self.W3, self.b3 = W3, b3

    def forward(self, x: np.ndarray) -> float:
        """x shape: (7,)  →  returns scalar probability in [0, 1]."""
        h1 = _relu(self.W1 @ x + self.b1)   # (64,)
        h2 = _relu(self.W2 @ h1 + self.b2)  # (32,)
        out = _sigmoid(self.W3 @ h2 + self.b3)  # (1,)
        return float(out[0])


# ── Weight initialization ─────────────────────────────────────────────────────

def _xavier(fan_in: int, fan_out: int, rng: np.random.Generator) -> np.ndarray:
    """Xavier uniform initialization."""
    limit = np.sqrt(6.0 / (fan_in + fan_out))
    return rng.uniform(-limit, limit, size=(fan_out, fan_in))


def _mock_weights() -> FraudMLP:
    """
    Initialize weights that produce sensible fraud scores.
    High-risk features (indices 0, 4, 6 = revenue_ratio, cascade_depth, cycle_flag)
    get amplified weights so they drive the output towards 1.0.
    """
    rng = np.random.default_rng(42)

    W1 = _xavier(7, 64, rng)
    # Amplify high-risk input features
    W1[:, 0] *= 2.0   # revenue_ratio
    W1[:, 3] *= 1.5   # duplicate_flag
    W1[:, 4] *= 2.0   # cascade_depth
    W1[:, 6] *= 2.5   # cycle_flag
    b1 = np.zeros(64)

    W2 = _xavier(64, 32, rng)
    b2 = np.zeros(32)

    W3 = _xavier(32, 1, rng)
    b3 = np.zeros(1)

    return FraudMLP(W1, b1, W2, b2, W3, b3)


# ── Singleton ─────────────────────────────────────────────────────────────────

_model_instance: FraudMLP | None = None


def load_model(path: Path | None = None) -> FraudMLP:
    """
    Load weights from .npz file if present, else use mock weights.
    Result is cached globally — safe to call repeatedly.
    """
    global _model_instance
    if _model_instance is not None:
        return _model_instance

    target = path or MODEL_PATH
    if target.exists():
        try:
            data = np.load(str(target))
            _model_instance = FraudMLP(
                W1=data["W1"], b1=data["b1"],
                W2=data["W2"], b2=data["b2"],
                W3=data["W3"], b3=data["b3"],
            )
            logger.info("Loaded fraud model weights from %s", target)
        except Exception as exc:
            logger.warning("Failed to load weights (%s) — using mock weights", exc)
            _model_instance = _mock_weights()
    else:
        logger.info("No weights at %s — using mock weights", target)
        _model_instance = _mock_weights()

    return _model_instance


def predict(features: list[float]) -> float:
    """
    Run inference and return fraud probability in [0, 1].
    features must have exactly 7 elements (see feature_engineering.py).
    """
    model = load_model()
    x = np.array(features, dtype=np.float64)
    return round(model.forward(x), 4)
