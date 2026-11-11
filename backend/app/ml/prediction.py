"""Inference service with stable model metadata and configurable thresholds."""
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from .data_loader import FEATURES


class ModelUnavailable(RuntimeError):
    """No trained model artifact is available."""


class PredictionService:
    def __init__(self, model_dir: str | Path, fraud_threshold: float | None = None,
                 high_risk_threshold: float = 0.9):
        self.model_dir = Path(model_dir)
        self.model = None
        self.metadata = {}
        self.fraud_threshold = fraud_threshold
        self.high_risk_threshold = high_risk_threshold
        self._metadata_mtime_ns = None
        self.load()

    def load(self) -> bool:
        metadata_path = self.model_dir / "active_model_metadata.joblib"
        if not metadata_path.exists():
            self.model = None
            self.metadata = {}
            self._metadata_mtime_ns = None
            return False
        try:
            metadata = joblib.load(metadata_path)
            model_path = Path(metadata["model_path"])
            if not model_path.is_absolute():
                model_path = self.model_dir / model_path
            if not model_path.is_file():
                self.model = None
                self.metadata = metadata
                return False
            model = joblib.load(model_path)
        except Exception:
            self.model = None
            self.metadata = {}
            return False
        self.metadata = metadata
        self.model = model
        self._metadata_mtime_ns = metadata_path.stat().st_mtime_ns
        return True

    def reload_if_changed(self) -> bool:
        """Load artifacts written or replaced after this service was created."""
        metadata_path = self.model_dir / "active_model_metadata.joblib"
        try:
            modified = metadata_path.stat().st_mtime_ns
        except FileNotFoundError:
            if self.available:
                self.model = None
                self.metadata = {}
                self._metadata_mtime_ns = None
            return False
        if modified != self._metadata_mtime_ns:
            return self.load()
        return self.available

    @property
    def available(self) -> bool:
        return self.model is not None

    def predict(self, rows) -> list[dict]:
        if not self.available: raise ModelUnavailable("No trained model is available. Place the Kaggle CSV and train a model.")
        frame = pd.DataFrame(rows)
        missing = set(FEATURES) - set(frame.columns)
        if missing: raise ValueError(f"Missing features: {', '.join(sorted(missing))}")
        frame = frame[FEATURES].apply(pd.to_numeric, errors="coerce")
        if frame.isna().any().any() or not np.isfinite(frame.to_numpy()).all(): raise ValueError("Features must be finite numeric values.")
        if (frame["Amount"] < 0).any() or (frame["Time"] < 0).any(): raise ValueError("Time and Amount must be non-negative.")
        probabilities = np.asarray(self.model.predict_proba(frame))[:, 1]
        threshold = self.fraud_threshold if self.fraud_threshold is not None else float(self.metadata.get("decision_threshold", 0.5))
        results = []
        for probability in probabilities:
            probability = float(probability)
            risk = "HIGH RISK" if probability >= self.high_risk_threshold else ("MEDIUM RISK" if probability >= threshold else "LOW RISK")
            results.append({"predicted_class": int(probability >= threshold), "fraud_probability": probability,
                            "risk_level": risk, "model_version": self.metadata.get("model_version", "unknown")})
        return results
