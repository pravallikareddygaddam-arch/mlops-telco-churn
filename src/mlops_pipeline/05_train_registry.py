




import os
import sys
import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import yaml

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)


def configure_mlflow(config):
    tracking_uri = (
        os.getenv("MLFLOW_TRACKING_URI")
        or config["mlflow"].get("tracking_uri")
    )

    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)


def train_and_register_model():

    print("[INFO] Starting MLflow training and registration...")

    with open("config.yaml", "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    configure_mlflow(config)

    mlflow.set_experiment(
        config["mlflow"]["experiment_name"]
    )

    processed_dir = config["data"]["processed_dir"]

    try:
        X_train = np.load(
            os.path.join(processed_dir, "X_train_final.npy")
        )

        X_test = np.load(
            os.path.join(processed_dir, "X_test_final.npy")
        )

        y_train = np.load(
            os.path.join(processed_dir, "y_train.npy")
        )

        y_test = np.load(
            os.path.join(processed_dir, "y_test.npy")
        )

    except FileNotFoundError as error:
        print("[ERROR] Processed data files not found.")
        print(error)
        return False

    model_cfg = config["model"]

    params = {
        "n_estimators": model_cfg["n_estimators"],
        "max_depth": model_cfg["max_depth"],
        "random_state": model_cfg["random_state"],
        "class_weight": model_cfg["class_weight"]
    }

    with mlflow.start_run(run_name="RandomForest") as run:

        mlflow.log_params(params)

        mlflow.log_param("model_family", "RandomForest")
        mlflow.log_param("lab", "Lab 10 and Lab 11")

        if os.getenv("GITHUB_RUN_ID"):
            mlflow.log_param(
                "github_run_id",
                os.getenv("GITHUB_RUN_ID")
            )

        if os.getenv("GITHUB_SHA"):
            mlflow.log_param(
                "github_commit",
                os.getenv("GITHUB_SHA")
            )

        print("[INFO] Training RandomForest model...")

        model = RandomForestClassifier(**params)
        model.fit(X_train, y_train)

        print("[INFO] Evaluating model...")

        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(
                y_test, y_pred, zero_division=0
            ),
            "recall": recall_score(
                y_test, y_pred, zero_division=0
            ),
            "f1_score": f1_score(
                y_test, y_pred, zero_division=0
            ),
            "roc_auc": roc_auc_score(y_test, y_proba)
        }

        mlflow.log_metrics(metrics)

        model_path = config["paths"]["model"]

        os.makedirs(
            os.path.dirname(model_path),
            exist_ok=True
        )

        joblib.dump(model, model_path)

        print(f"[SUCCESS] Model saved to {model_path}")

        preprocessor_path = config["paths"]["preprocessor"]

        if os.path.exists(preprocessor_path):

            mlflow.log_artifact(
                preprocessor_path,
                artifact_path="preprocessing_pipeline"
            )

            print("[SUCCESS] Preprocessor logged.")

        else:
            print("[WARNING] Preprocessor file not found.")

        print("[INFO] Registering model in MLflow...")

        mlflow.sklearn.log_model(
            sk_model=model,
            name="random_forest_model",
            registered_model_name=config["registry"]["model_name"],
            serialization_format="pickle"
        )

        print("\n========== TRAINING RESULTS ==========")

        for metric, value in metrics.items():
            print(f"{metric}: {value:.4f}")

        print("\n[SUCCESS] Model registered successfully.")

        print(
            f"[INFO] Registered Model Name: "
            f"{config['registry']['model_name']}"
        )

        print(f"[INFO] MLflow Run ID: {run.info.run_id}")

        print("======================================")

    return True


if __name__ == "__main__":

    success = train_and_register_model()

    sys.exit(0 if success else 1)
