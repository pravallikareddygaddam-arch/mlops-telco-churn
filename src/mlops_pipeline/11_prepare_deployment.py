
import json
import os
import shutil
import joblib
import mlflow
import mlflow.sklearn
import yaml

from pathlib import Path
from mlflow.tracking import MlflowClient
from datetime import datetime, timezone


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_config():
    config_path = PROJECT_ROOT / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}"
        )

    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def configure_mlflow(config):
    tracking_uri = (
        os.getenv("MLFLOW_TRACKING_URI")
        or config["mlflow"]["tracking_uri"]
    )

    mlflow.set_tracking_uri(tracking_uri)

    print("[INFO] MLflow Tracking URI:", tracking_uri)


def get_latest_registered_model(client, model_name):

    print(f"[INFO] Searching registered model: {model_name}")

    try:
        versions = list(
            client.search_model_versions(
                f"name='{model_name}'"
            )
        )

        if not versions:
            raise RuntimeError(
                f"No registered versions found for {model_name}"
            )

        latest_version = max(
            versions,
            key=lambda version: int(version.version)
        )

        print(
            f"[SUCCESS] Latest registered version: "
            f"{latest_version.version}"
        )

        return latest_version

    except Exception as error:
        raise RuntimeError(
            f"Could not find registered model '{model_name}': {error}"
        )


def prepare_deployment():

    print("=" * 60)
    print("LAB 11 - PREPARE DEPLOYMENT")
    print("=" * 60)

    # Step 1: Load configuration
    config = load_config()

    # Step 2: Configure MLflow
    configure_mlflow(config)

    client = MlflowClient()

    # Step 3: Read registered model name from config
    model_name = config["registry"]["model_name"]

    # Step 4: Find latest registered model version
    model_version = get_latest_registered_model(
        client,
        model_name
    )

    model_uri = (
        f"models:/{model_name}/{model_version.version}"
    )

    print("[INFO] Model URI:", model_uri)

    # Step 5: Load model from MLflow
    print("[INFO] Loading registered model...")

    model = mlflow.sklearn.load_model(model_uri)

    print("[SUCCESS] Registered model loaded.")

    # Step 6: Create deployment directory
    deployment_dir = PROJECT_ROOT / "deployment"

    deployment_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    # Step 7: Save deployment model
    deployment_model_path = (
        deployment_dir / "model.pkl"
    )

    joblib.dump(
        model,
        deployment_model_path
    )

    print(
        "[SUCCESS] Model saved:",
        deployment_model_path
    )

    # Step 8: Copy preprocessor
    preprocessor_source = (
        PROJECT_ROOT / config["paths"]["preprocessor"]
    )

    if not preprocessor_source.exists():
        raise FileNotFoundError(
            f"Preprocessor not found: {preprocessor_source}"
        )

    preprocessor_destination = (
        deployment_dir / "preprocessor.pkl"
    )

    shutil.copy2(
        preprocessor_source,
        preprocessor_destination
    )

    print("[SUCCESS] Preprocessor copied.")

    # Step 9: Create deployment metadata
    metadata = {
        "project": config["project"]["name"],
        "project_version": config["project"]["version"],
        "model_name": model_name,
        "model_version": str(model_version.version),
        "model_source": model_uri,
        "deployment_status": "READY",
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "model_file": "model.pkl",
        "preprocessor_file": "preprocessor.pkl"
    }

    metadata_path = (
        deployment_dir / "model_metadata.json"
    )

    with open(
        metadata_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4
        )

    print("[SUCCESS] Deployment metadata saved.")

    # Step 10: Verify deployment artifacts
    required_files = [
        deployment_model_path,
        preprocessor_destination,
        metadata_path
    ]

    for file_path in required_files:

        if not file_path.exists():
            raise FileNotFoundError(
                f"Deployment artifact missing: {file_path}"
            )

        print("[VERIFIED]", file_path.relative_to(PROJECT_ROOT))

    print("\n" + "=" * 60)
    print("LAB 11 DEPLOYMENT PREPARATION PASSED!")
    print("=" * 60)


if __name__ == "__main__":

    try:
        prepare_deployment()

    except Exception as error:
        print("\n[ERROR]", error)
        raise
