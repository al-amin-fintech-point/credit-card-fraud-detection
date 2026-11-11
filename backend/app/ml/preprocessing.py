"""Leakage-safe feature preprocessing."""
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from .data_loader import FEATURES


def make_preprocessor() -> ColumnTransformer:
    """Scale every numeric input using training-fold statistics only.

    This keeps elapsed Time and PCA component magnitudes compatible with
    distance-based resampling and Logistic Regression. Tree models are
    invariant to monotonic feature scaling.
    """
    return ColumnTransformer([("numeric", StandardScaler(), FEATURES)],
                             remainder="drop", verbose_feature_names_out=False)


def make_pipeline(estimator) -> Pipeline:
    """Build a pipeline so scaling is fitted only on each training fold."""
    return Pipeline([("preprocess", make_preprocessor()), ("model", estimator)])
