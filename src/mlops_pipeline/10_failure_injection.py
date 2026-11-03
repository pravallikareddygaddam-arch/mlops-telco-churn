
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
import numpy as np
import pandas as pd
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def configure_mlflow(config):
    tracking_uri = (
        os.getenv("MLFLOW_TRACKING_URI")
        or config["mlflow"].get("tracking_uri")
    )

    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)


def run_script(script_path):
    script = PROJECT_ROOT / script_path

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=PROJECT_ROOT
    )

    return result.returncode


def restore_file(backup_path, original_path):
    if os.path.exists(original_path):
        os.remove(original_path)

    os.replace(backup_path, original_path)


def make_result(scenario, expected, actual, passed, **extra):
    result = {
        "scenario": scenario,
        "expected": expected,
        "actual": actual,
        "passed": passed
    }
    result.update(extra)
    return result


# SCENARIO 1: MISSING DATA

def test_missing_data(config):
    print("\n[LAB 10] Scenario 1: Missing data")

    data_path = PROJECT_ROOT / config["data"]["raw_path"]
    backup_path = Path(str(data_path) + ".lab10_backup")

    if not data_path.exists():
        return make_result(
            "missing_data", "HALT", "NOT_TESTED", False
        )

    os.replace(data_path, backup_path)

    try:
        exit_code = run_script(
            "src/mlops_pipeline/02_validate_data.py"
        )

        passed = exit_code != 0

        return make_result(
            "missing_data",
            "HALT",
            "HALT" if passed else "CONTINUED",
            passed
        )
    finally:
        restore_file(backup_path, data_path)


# SCENARIO 2: INVALID DATATYPE

def test_invalid_datatype(config):
    print("\n[LAB 10] Scenario 2: Invalid datatype")

    data_path = PROJECT_ROOT / config["data"]["raw_path"]
    backup_path = Path(str(data_path) + ".lab10_backup")

    shutil.copy2(data_path, backup_path)

    try:
        df = pd.read_csv(data_path)

        df["MonthlyCharges"] = df["MonthlyCharges"].astype(object)
        df.loc[0, "MonthlyCharges"] = "INVALID_NUMBER"

        df.to_csv(data_path, index=False)

        exit_code = run_script(
            "src/mlops_pipeline/02_validate_data.py"
        )

        passed = exit_code != 0

        return make_result(
            "invalid_datatype",
            "HALT",
            "HALT" if passed else "CONTINUED",
            passed
        )
    finally:
        restore_file(backup_path, data_path)


# SCENARIO 3: SCHEMA MISMATCH

def test_schema_mismatch(config):
    print("\n[LAB 10] Scenario 3: Schema mismatch")

    data_path = PROJECT_ROOT / config["data"]["raw_path"]
    backup_path = Path(str(data_path) + ".lab10_backup")

    shutil.copy2(data_path, backup_path)

    try:
        df = pd.read_csv(data_path)

        df = df.drop(columns=["Contract"])
        df.to_csv(data_path, index=False)

        exit_code = run_script(
            "src/mlops_pipeline/02_validate_data.py"
        )

        passed = exit_code != 0

        return make_result(
            "schema_mismatch",
            "HALT",
            "HALT" if passed else "CONTINUED",
            passed
        )
    finally:
        restore_file(backup_path, data_path)


# SCENARIO 4: PREPROCESSING INCONSISTENCY

def test_preprocessing_inconsistency(config):
    print("\n[LAB 10] Scenario 4: Preprocessing inconsistency")

    processed_dir = PROJECT_ROOT / config["data"]["processed_dir"]
    data_path = processed_dir / "X_train_final.npy"
    backup_path = Path(str(data_path) + ".lab10_backup")

    if not data_path.exists():
        return make_result(
            "preprocessing_inconsistency",
            "HALT",
            "NOT_TESTED",
            False
        )

    shutil.copy2(data_path, backup_path)

    try:
        X_train = np.load(data_path)

        X_train[0, 0] = np.nan
        np.save(data_path, X_train)

        exit_code = run_script(
            "src/mlops_pipeline/04_validate_outputs.py"
        )

        passed = exit_code != 0

        return make_result(
            "preprocessing_inconsistency",
            "HALT",
            "HALT" if passed else "CONTINUED",
            passed
        )
    finally:
        restore_file(backup_path, data_path)


# SCENARIO 5: MISSING MODEL AND RECOVERY

def test_missing_model_with_recovery(config):
    print("\n[LAB 10] Scenario 5: Missing model and recovery")

    model_path = PROJECT_ROOT / config["paths"]["model"]
    model_name = config["registry"]["model_name"]

    if not model_path.exists():
        return make_result(
            "missing_model_artifact",
            "RECOVER",
            "NOT_TESTED",
            False
        )

    backup_path = Path(str(model_path) + ".lab10_backup")
    shutil.copy2(model_path, backup_path)

    os.remove(model_path)

    try:
        print("[INFO] Checking missing model detection...")

        failure_exit_code = run_script(
            "src/mlops_pipeline/06_model_evaluation.py"
        )

        failure_detected = failure_exit_code != 0

        configure_mlflow(config)

        print("[INFO] Searching MLflow model registry...")

        client = MlflowClient()

        versions = client.search_model_versions(
            f"name='{model_name}'"
        )

        if not versions:
            raise RuntimeError(
                f"No registered versions found for {model_name}"
            )

        latest_version = max(
            versions,
            key=lambda version: int(version.version)
        )

        model_uri = (
            f"models:/{model_name}/{latest_version.version}"
        )

        print(f"[INFO] Loading model: {model_uri}")

        recovered_model = mlflow.sklearn.load_model(model_uri)

        model_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        joblib.dump(recovered_model, model_path)

        print("[SUCCESS] Model recovered from MLflow.")

        print("[INFO] Evaluating recovered model...")

        recovery_exit_code = run_script(
            "src/mlops_pipeline/06_model_evaluation.py"
        )

        recovered = recovery_exit_code == 0
        passed = failure_detected and recovered

        return make_result(
            "missing_model_artifact",
            "RECOVER",
            "RECOVERED" if passed else "RECOVERY_FAILED",
            passed,
            failure_detected=failure_detected,
            recovery_succeeded=recovered,
            recovered_model_version=latest_version.version
        )

    except Exception as error:
        print(f"[ERROR] Recovery failed: {error}")

        return make_result(
            "missing_model_artifact",
            "RECOVER",
            "RECOVERY_FAILED",
            False,
            error=str(error)
        )

    finally:
        restore_file(backup_path, model_path)


# MAIN EXECUTION

def run_failure_tests():
    print("\n==============================================")
    print("LAB 10 - FAILURE HANDLING AND RECOVERY")
    print("==============================================")

    config_path = PROJECT_ROOT / "config.yaml"

    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    configure_mlflow(config)

    repetitions = int(config.get("lab9", {}).get("repetitions", 1))

    tests = [
        test_missing_data,
        test_invalid_datatype,
        test_schema_mismatch,
        test_preprocessing_inconsistency,
        test_missing_model_with_recovery
    ]

    all_runs = []

    for repetition in range(1, repetitions + 1):
        print(f"\n[INFO] Repetition {repetition}/{repetitions}")

        results = []

        for test in tests:
            try:
                result = test(config)
            except Exception as error:
                print(f"[ERROR] {test.__name__}: {error}")

                result = make_result(
                    test.__name__,
                    "SUCCESS",
                    "ERROR",
                    False,
                    error=str(error)
                )

            results.append(result)

            print(
                "[RESULT]",
                result["scenario"],
                "PASSED" if result["passed"] else "FAILED"
            )

        all_runs.append({
            "repetition": repetition,
            "results": results,
            "passed": all(item["passed"] for item in results)
        })

    report = {
        "stage": "Lab 10 Failure Handling and Recovery",
        "repetitions": repetitions,
        "runs": all_runs,
        "overall_status": (
            "PASSED"
            if all(run["passed"] for run in all_runs)
            else "FAILED"
        )
    }

    report_path = (
        PROJECT_ROOT / config["paths"]["failure_report"]
    )

    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print("\n==============================================")
    print("LAB 10 FINAL STATUS:", report["overall_status"])
    print("Report saved:", report_path)
    print("==============================================")

    return report["overall_status"] == "PASSED"


if __name__ == "__main__":
    success = run_failure_tests()
    sys.exit(0 if success else 1)
