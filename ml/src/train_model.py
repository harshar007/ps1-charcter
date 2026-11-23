"""
Training script for the RetroMorph AI Image Readiness Classifier.
Trains an interpretable, robust ensemble model (Random Forest Pipeline)
on extracted computer vision features and serializes it to a .pkl artifact.
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, f1_score

# Ensure ml/src is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

from features import FEATURE_NAMES


def train_model(
    data_path: str = "ml/data/dataset.csv",
    artifact_path: str = "ml/artifacts/image_quality_model.pkl",
    backend_model_path: str = "backend/models/image_quality_model.pkl",
):
    print(f"Loading dataset from: {data_path}")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found at {data_path}. Run generate_dataset.py first.")

    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} samples.")
    print("Class distribution:\n", df["label"].value_counts())

    X = df[FEATURE_NAMES]
    y = df["label"]

    # Stratified 80/20 train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print(f"Train size: {len(X_train)} | Test size: {len(X_test)}")

    # Construct ML Pipeline with feature scaling + Random Forest
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", RandomForestClassifier(
            n_estimators=100,
            max_depth=6,
            min_samples_split=4,
            min_samples_leaf=2,
            random_state=42
        ))
    ])

    # 5-Fold Cross Validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="f1_macro")
    print(f"5-Fold Cross Validation Macro F1: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

    # Fit final pipeline on all training data
    pipeline.fit(X_train, y_train)

    # Test set predictions
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="macro")

    print("\n=== Test Set Performance ===")
    print(f"Accuracy: {acc:.4f}")
    print(f"Macro F1: {f1:.4f}")
    print("\nClassification Report:\n", classification_report(y_test, y_pred))

    # Feature Importance analysis
    rf = pipeline.named_steps["classifier"]
    importances = dict(zip(FEATURE_NAMES, rf.feature_importances_))
    sorted_importances = sorted(importances.items(), key=lambda x: x[1], reverse=True)
    print("Top Feature Importances:")
    for feat, imp in sorted_importances:
        print(f"  - {feat:25s}: {imp:.4f}")

    # Build metadata envelope
    import sklearn
    model_artifact = {
        "pipeline": pipeline,
        "feature_names": FEATURE_NAMES,
        "classes": list(pipeline.classes_),
        "created_at": datetime.now().isoformat(),
        "sklearn_version": sklearn.__version__,
        "metrics": {
            "cv_macro_f1": float(cv_scores.mean()),
            "cv_macro_f1_std": float(cv_scores.std()),
            "test_accuracy": float(acc),
            "test_macro_f1": float(f1),
        },
        "feature_importances": importances,
    }

    # Save artifact
    os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
    joblib.dump(model_artifact, artifact_path)
    print(f"\nSaved model artifact to: {artifact_path}")

    # Also copy to backend models directory
    os.makedirs(os.path.dirname(backend_model_path), exist_ok=True)
    joblib.dump(model_artifact, backend_model_path)
    print(f"Copied model artifact to backend: {backend_model_path}")

    # Save split datasets for evaluation script and notebook
    test_df = X_test.copy()
    test_df["label"] = y_test
    test_df.to_csv("ml/data/test_split.csv", index=False)
    
    return model_artifact


if __name__ == "__main__":
    train_model()
