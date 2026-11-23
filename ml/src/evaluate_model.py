"""
Evaluation script for the RetroMorph AI Image Readiness Classifier.
Loads the serialized .pkl model, tests on held-out data, and outputs
metrics and a confusion matrix to ml/reports/evaluation_metrics.json.
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, roc_auc_score, classification_report
)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from features import FEATURE_NAMES


def evaluate_model(
    artifact_path: str = "ml/artifacts/image_quality_model.pkl",
    test_data_path: str = "ml/data/test_split.csv",
    report_output_path: str = "ml/reports/evaluation_metrics.json"
):
    print(f"Loading artifact from {artifact_path}...")
    if not os.path.exists(artifact_path):
        raise FileNotFoundError(f"Model artifact not found at {artifact_path}. Run train_model.py first.")

    artifact = joblib.load(artifact_path)
    pipeline = artifact["pipeline"]
    feature_names = artifact.get("feature_names", FEATURE_NAMES)

    if not os.path.exists(test_data_path):
        # Fallback to full dataset
        test_data_path = "ml/data/dataset.csv"
        
    print(f"Loading test evaluation data from {test_data_path}...")
    df = pd.read_csv(test_data_path)
    X_test = df[feature_names]
    y_test = df["label"]

    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)

    # Calculate metrics
    acc = float(accuracy_score(y_test, y_pred))
    p, r, f1, s = precision_recall_fscore_support(y_test, y_pred, average=None, labels=pipeline.classes_)
    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(y_test, y_pred, average="macro")
    
    cm = confusion_matrix(y_test, y_pred, labels=pipeline.classes_)

    # ROC AUC (binary)
    pos_idx = list(pipeline.classes_).index("ready")
    auc = float(roc_auc_score((y_test == "ready").astype(int), y_proba[:, pos_idx]))

    per_class_metrics = {}
    for i, cls in enumerate(pipeline.classes_):
        per_class_metrics[cls] = {
            "precision": round(float(p[i]), 4),
            "recall": round(float(r[i]), 4),
            "f1_score": round(float(f1[i]), 4),
            "support": int(s[i]),
        }

    metrics = {
        "model_artifact": artifact_path,
        "evaluation_dataset": test_data_path,
        "sample_count": len(df),
        "overall_accuracy": round(acc, 4),
        "macro_precision": round(float(macro_p), 4),
        "macro_recall": round(float(macro_r), 4),
        "macro_f1_score": round(float(macro_f1), 4),
        "roc_auc_score": round(auc, 4),
        "classes": list(pipeline.classes_),
        "per_class": per_class_metrics,
        "confusion_matrix": {
            "labels": list(pipeline.classes_),
            "matrix": cm.tolist()
        },
        "feature_importances": artifact.get("feature_importances", {})
    }

    print("\n==========================================")
    print("      IMAGE READINESS MODEL EVALUATION    ")
    print("==========================================")
    print(f"Test Accuracy:    {acc * 100:.2f}%")
    print(f"Macro F1-Score:   {macro_f1:.4f}")
    print(f"ROC AUC:          {auc:.4f}")
    print("\nConfusion Matrix:")
    print(f"{'':10s} Pred: {pipeline.classes_[0]:10s} Pred: {pipeline.classes_[1]:10s}")
    for idx, row_cls in enumerate(pipeline.classes_):
        print(f"True {row_cls:7s} {cm[idx][0]:<15d} {cm[idx][1]:<15d}")
    print("\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred))

    os.makedirs(os.path.dirname(report_output_path), exist_ok=True)
    with open(report_output_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved evaluation metrics report to: {report_output_path}")

    return metrics


if __name__ == "__main__":
    evaluate_model()
