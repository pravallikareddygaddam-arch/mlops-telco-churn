import os
import json
import joblib
import numpy as np

import mlflow
import mlflow.sklearn

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    roc_curve
)


def train_and_track(run_name="RandomForest"):

    print(f"\n--- Starting MLflow Run: {run_name} ---")

    os.makedirs("artifacts", exist_ok=True)
    os.makedirs("models", exist_ok=True)

    mlflow.set_experiment("Telco_Churn_Prediction")

    X_train = np.load(
        "data/processed/X_train_final.npy"
    )

    X_test = np.load(
        "data/processed/X_test_final.npy"
    )

    y_train = np.load(
        "data/processed/y_train.npy"
    )

    y_test = np.load(
        "data/processed/y_test.npy"
    )

    with mlflow.start_run(run_name=run_name):

        # ==========================================
        # MODEL
        # ==========================================

        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight="balanced"
        )

        mlflow.log_params({
            "model": "RandomForest",
            "n_estimators": 100,
            "max_depth": 10,
            "random_state": 42,
            "class_weight": "balanced"
        })

        model.fit(
            X_train,
            y_train
        )

        # ==========================================
        # PREDICTION
        # ==========================================

        y_pred = model.predict(
            X_test
        )

        y_proba = model.predict_proba(
            X_test
        )[:, 1]

        # ==========================================
        # METRICS
        # ==========================================

        accuracy = accuracy_score(
            y_test,
            y_pred
        )

        precision = precision_score(
            y_test,
            y_pred
        )

        recall = recall_score(
            y_test,
            y_pred
        )

        f1 = f1_score(
            y_test,
            y_pred
        )

        roc_auc = roc_auc_score(
            y_test,
            y_proba
        )

        mlflow.log_metrics({
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "roc_auc": roc_auc
        })

        print(
            f"Metrics logged: "
            f"F1 = {f1:.4f} | "
            f"ROC-AUC = {roc_auc:.4f}"
        )

        # ==========================================
        # CONFUSION MATRIX
        # ==========================================

        cm = confusion_matrix(
            y_test,
            y_pred
        )

        fig_cm = Figure(
            figsize=(6, 5)
        )

        canvas_cm = FigureCanvasAgg(
            fig_cm
        )

        ax_cm = fig_cm.add_subplot(111)

        ax_cm.imshow(cm)

        ax_cm.set_title(
            "Confusion Matrix"
        )

        ax_cm.set_xlabel(
            "Predicted"
        )

        ax_cm.set_ylabel(
            "Actual"
        )

        ax_cm.set_xticks([0, 1])
        ax_cm.set_yticks([0, 1])

        for i in range(2):
            for j in range(2):

                ax_cm.text(
                    j,
                    i,
                    str(cm[i, j]),
                    ha="center",
                    va="center"
                )

        fig_cm.tight_layout()

        cm_path = (
            "artifacts/confusion_matrix.png"
        )

        canvas_cm.print_png(
            cm_path
        )

        mlflow.log_artifact(
            cm_path,
            artifact_path="plots"
        )

        # ==========================================
        # ROC CURVE
        # ==========================================

        fpr, tpr, _ = roc_curve(
            y_test,
            y_proba
        )

        fig_roc = Figure(
            figsize=(6, 5)
        )

        canvas_roc = FigureCanvasAgg(
            fig_roc
        )

        ax_roc = fig_roc.add_subplot(111)

        ax_roc.plot(
            fpr,
            tpr
        )

        ax_roc.plot(
            [0, 1],
            [0, 1],
            linestyle="--"
        )

        ax_roc.set_title(
            "ROC Curve"
        )

        ax_roc.set_xlabel(
            "False Positive Rate"
        )

        ax_roc.set_ylabel(
            "True Positive Rate"
        )

        fig_roc.tight_layout()

        roc_path = (
            "artifacts/roc_curve.png"
        )

        canvas_roc.print_png(
            roc_path
        )

        mlflow.log_artifact(
            roc_path,
            artifact_path="plots"
        )

        # ==========================================
        # DATASET METADATA
        # ==========================================

        metadata_path = (
            "data/processed/"
            "dataset_metadata.json"
        )

        if os.path.exists(metadata_path):

            mlflow.log_artifact(
                metadata_path,
                artifact_path="metadata"
            )

        # ==========================================
        # SAVE MODEL TO MLFLOW
        # ==========================================

        mlflow.sklearn.log_model(
            sk_model=model,
            name="model",
            skops_trusted_types=[
                "sklearn.tree._tree.Tree"
            ]
        )

        # ==========================================
        # LOCAL MODEL BACKUP
        # ==========================================

        joblib.dump(
            model,
            "models/random_forest_model.pkl"
        )

        print(
            "MLflow tracking completed successfully!"
        )

        print(
            "Confusion matrix saved successfully!"
        )

        print(
            "ROC curve saved successfully!"
        )

        print(
            "Model saved successfully!"
        )


if __name__ == "__main__":

    train_and_track(
        run_name="RandomForest"
    )