"""Train, compare, select, and persist models using real Kaggle data."""
from datetime import datetime, timezone
import json
from pathlib import Path
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.base import clone
from sklearn.tree import DecisionTreeClassifier
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbalancedPipeline
from imblearn.under_sampling import RandomUnderSampler
from xgboost import XGBClassifier
from .data_loader import FEATURES, TARGET, load_dataset, dataset_summary
from .preprocessing import make_pipeline, make_preprocessor


def train(dataset_path: str | Path, artifact_dir: str | Path, seed: int = 42) -> dict:
    """Compare four classifiers; evaluate final winner once on held-out test data."""
    frame = load_dataset(dataset_path)
    original_summary = dataset_summary(frame)
    # Remove only exact duplicates after recording their prevalence in summary.
    frame = frame.drop_duplicates().reset_index(drop=True)
    x, y = frame[FEATURES], frame[TARGET].astype(int)
    x_train_val, x_test, y_train_val, y_test = train_test_split(
        x, y, test_size=0.15, random_state=seed, stratify=y)
    x_train, x_val, y_train, y_val = train_test_split(
        x_train_val, y_train_val, test_size=0.1765, random_state=seed, stratify=y_train_val)
    imbalance = float((y_train == 0).sum() / max(1, (y_train == 1).sum()))
    candidates = {
        "logistic_regression_weighted": (LogisticRegression(class_weight="balanced", max_iter=2000, random_state=seed), None),
        "logistic_regression_undersampled": (LogisticRegression(max_iter=1000, random_state=seed), "undersample"),
        "logistic_regression_smote": (LogisticRegression(max_iter=1000, random_state=seed), "smote"),
        "decision_tree": (DecisionTreeClassifier(class_weight="balanced", min_samples_leaf=2, random_state=seed), None),
        "random_forest": (RandomForestClassifier(n_estimators=300, class_weight="balanced_subsample",
                                                 min_samples_leaf=2, n_jobs=-1, random_state=seed), None),
        "xgboost": (XGBClassifier(n_estimators=350, max_depth=5, learning_rate=0.05,
                                 subsample=0.85, colsample_bytree=0.85, reg_lambda=2,
                                 scale_pos_weight=imbalance, eval_metric="aucpr", n_jobs=-1,
                                 random_state=seed), None),
    }
    validation = {}
    for name, (model, sampling) in candidates.items():
        pipeline = _training_pipeline(model, sampling, seed, y_train)
        pipeline.fit(x_train, y_train)
        probabilities = pipeline.predict_proba(x_val)[:, 1]
        thresholds = np.linspace(0.05, 0.95, 91)
        f1s = [evaluate_at_threshold(y_val.to_numpy(), probabilities, t)["f1"] for t in thresholds]
        threshold = float(thresholds[int(np.argmax(f1s))])
        metrics = evaluate_at_threshold(y_val.to_numpy(), probabilities, threshold)
        validation[name] = {"metrics": metrics, "decision_threshold": threshold,
                            "threshold_f1": metrics["f1"]}
    # Primary ranking is validation PR-AUC; F1 breaks close ties as PR-AUC measures rare-class ranking.
    winner = max(validation, key=lambda n: (validation[n]["metrics"]["pr_auc"], validation[n]["threshold_f1"]))
    threshold = validation[winner]["decision_threshold"]
    selected_model, selected_sampling = candidates[winner]
    best = _training_pipeline(clone(selected_model), selected_sampling, seed, y_train_val)
    best.fit(x_train_val, y_train_val)
    test_metrics = evaluate_at_threshold(y_test.to_numpy(), best.predict_proba(x_test)[:, 1], threshold)
    version = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = Path(artifact_dir); out.mkdir(parents=True, exist_ok=True)
    model_path = out / f"fraud_model_{version}.joblib"
    preprocessing_path = out / f"preprocessing_{version}.joblib"
    joblib.dump(best, model_path)
    joblib.dump(best.named_steps["preprocess"], preprocessing_path)
    report = {"model_name": winner, "model_version": version, "trained_at": datetime.now(timezone.utc).isoformat(),
              "dataset_summary": original_summary, "split_sizes": {"train": len(x_train), "validation": len(x_val), "test": len(x_test)},
              "selection_metric": "validation PR-AUC, threshold F1 as tie breaker",
              "imbalance_strategies": "Class-weighted baselines compared with random undersampling and SMOTE for logistic regression. Resampling is inside the training pipeline and is fitted on training rows only; SMOTEENN was not added without evidence it improves this dataset.",
              "decision_threshold": threshold, "validation": validation, "test": test_metrics,
              "features": FEATURES, "model_path": model_path.name,
              "preprocessing_path": preprocessing_path.name}
    (out / "metrics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    joblib.dump({"model_path": model_path.name, "model_name": winner, "model_version": version,
                 "decision_threshold": threshold, "features": FEATURES,
                 "preprocessing_path": preprocessing_path.name}, out / "active_model_metadata.joblib")
    return report


def _training_pipeline(estimator, sampling: str | None, seed: int, y_train):
    """Place optional resampling after preprocessing, inside training-only fit."""
    if sampling is None:
        return make_pipeline(estimator)
    if sampling == "undersample":
        sampler = RandomUnderSampler(random_state=seed)
    else:
        negatives = int((np.asarray(y_train) == 0).sum())
        positives = int((np.asarray(y_train) == 1).sum())
        current_ratio = positives / max(1, negatives)
        sampling_ratio = min(1.0, max(0.15, current_ratio * 1.1))
        sampler = SMOTE(random_state=seed, sampling_strategy=sampling_ratio)
    return ImbalancedPipeline([("preprocess", make_preprocessor()), ("sampler", sampler), ("model", estimator)])


def evaluate_at_threshold(y_true, probabilities, threshold: float) -> dict:
    """Evaluate probabilities at a configured decision threshold."""
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, average_precision_score, confusion_matrix, classification_report
    pred = (np.asarray(probabilities) >= threshold).astype(int)
    return {"accuracy": float(accuracy_score(y_true, pred)),
            "precision": float(precision_score(y_true, pred, zero_division=0)),
            "recall": float(recall_score(y_true, pred, zero_division=0)),
            "f1": float(f1_score(y_true, pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_true, probabilities)),
            "pr_auc": float(average_precision_score(y_true, probabilities)),
            "confusion_matrix": confusion_matrix(y_true, pred).tolist(),
            "classification_report": classification_report(y_true, pred, output_dict=True, zero_division=0)}
