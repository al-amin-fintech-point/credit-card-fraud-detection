"""Imbalance-aware evaluation helpers."""
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             roc_auc_score, average_precision_score, confusion_matrix,
                             classification_report)


def evaluate(estimator, x, y) -> dict:
    pred = estimator.predict(x)
    probability = estimator.predict_proba(x)[:, 1]
    return {"accuracy": float(accuracy_score(y, pred)),
            "precision": float(precision_score(y, pred, zero_division=0)),
            "recall": float(recall_score(y, pred, zero_division=0)),
            "f1": float(f1_score(y, pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y, probability)),
            "pr_auc": float(average_precision_score(y, probability)),
            "confusion_matrix": confusion_matrix(y, pred).tolist(),
            "classification_report": classification_report(y, pred, output_dict=True, zero_division=0)}
