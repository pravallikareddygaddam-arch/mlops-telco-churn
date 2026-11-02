
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
import yaml


# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]


# Configure MLflow
def configure_mlflow(config):

    tracking_uri = (
        os.getenv("MLFLOW_TRACKING_URI")
        or config["mlflow"].get("tracking_uri")
    )

    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)


# Execute project scripts
def run_script(script_path):

    script = PROJECT_ROOT / script_path

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=PROJECT_ROOT
    )

    return result.returncode


# Restore original files
def restore_file(backup_path, original_path):

    if os.path.exists(original_path):
        os.remove(original_path)

    os.replace(backup_path, original_path)


# ==========================================================
# SCENARIO 1: MISSING DATA
# ==========================================================

def test_missing_data(config):

    print("\n[LAB 10] Scenario 1: Missing data")

    data_path = PROJECT_ROOT / config["data"]["raw_path"]

    backup_path = Path(
        str(data_path) + ".lab10_backup"
    )

    if not data_path.exists():

        print("[ERROR] Dataset not found.")

        return {
            "scenario": "missing_data",
            "expected": "HALT",
            "actual": "NOT_TESTED",
            "passed": False
        }

    os.replace(data_path, backup_path)

    try:

        exit_code = run_script(
            "src/mlops_pipeline/02_validate_data.py"
        )

        passed = exit_code != 0

        return {
            "scenario": "missing_data",
            "expected": "HALT",
            "actual": "HALT" if passed else "CONTINUED",
            "passed": passed
        }

    finally:

        restore_file(
            backup_path,
            data_path
        )


# ==========================================================
# SCENARIO 2: INVALID DATATYPE
# ==========================================================

def test_invalid_datatype(config):

    print("\n[LAB 10] Scenario 2: Invalid datatype")

    data_path = PROJECT_ROOT / config["data"]["raw_path"]

    backup_path = Path(
        str(data_path) + ".lab10_backup"
    )

    shutil.copy2(data_path, backup_path)

    try:

        df = pd.read_csv(data_path)

        df["MonthlyCharges"] = (
            df["MonthlyCharges"].astype(object)
        )

        df.loc[0, "MonthlyCharges"] = "INVALID_NUMBER"

        df.to_csv(data_path, index=False)

        exit_code = run_script(
            "src/mlops_pipeline/02_validate_data.py"
        )

        passed = exit_code != 0

        return {
            "scenario": "invalid_datatype",
            "expected": "HALT",
            "actual": "HALT" if passed else "CONTINUED",
            "passed": passed
        }

    finally:

        restore_file(
            backup_path,
            data_path
        )


# ==========================================================
# SCENARIO 3: SCHEMA MISMATCH
# ==========================================================

def test_schema_mismatch(config):

    print("\n[LAB 10] Scenario 3: Schema mismatch")

    data_path = PROJECT_ROOT / config["data"]["raw_path"]

    backup_path = Path(
        str(data_path) + ".lab10_backup"
    )

    shutil.copy2(data_path, backup_path)

    try:

        df = pd.read_csv(data_path)

        df = df.drop(columns=["Contract"])

        df.to_csv(data_path, index=False)

        exit_code = run_script(
            "src/mlops_pipeline/02_validate_data.py"
        )

        passed = exit_code != 0

        return {
            "scenario": "schema_mismatch",
            "expected": "HALT",
            "actual": "HALT" if passed else "CONTINUED",
            "passed": passed
        }

    finally:

        restore_file(
            backup_path,
            data_path
        )


# ==========================================================
# SCENARIO 4: PREPROCESSING INCONSISTENCY
# ==========================================================

def test_preprocessing_inconsistency(config):

    print("\n[LAB 10] Scenario 4: Preprocessing inconsistency")

    processed_dir = PROJECT_ROOT / config["data"]["processed_dir"]

    path = processed_dir / "X_train_final.npy"

    backup_path = Path(
        str(path) + ".lab10_backup"
    )

    if not path.exists():

        print("[ERROR] Processed training data not found.")

        return {
            "scenario": "preprocessing_inconsistency",
            "expected": "HALT",
            "actual": "NOT_TESTED",
            "passed": False
        }

    shutil.copy2(path, backup_path)

    try:

        X_train = np.load(path)

        # Inject NaN to simulate preprocessing failure
        X_train[0, 0] = np.nan

        np.save(path, X_train)

        exit_code = run_script(
            "src/mlops_pipeline/04_validate_outputs.py"
        )

        passed = exit_code != 0

        return {
            "scenario": "preprocessing_inconsistency",
            "expected": "HALT",
            "actual": "HALT" if passed else "CONTINUED",
            "passed": passed
        }

    finally:

        restore_file(
            backup_path,
            path
        )


# ==========================================================
# SCENARIO 5: MISSING MODEL + RECOVERY FROM MLFLOW
# ==========================================================

def test_missing_model_with_recovery(config):

    print(
        "\n[LAB 10] Scenario 5: "
        "Missing model artifact + recovery"
    )

    model_path = PROJECT_ROOT / config["paths"]["model"]

    model_name = config["registry"]["model_name"]

    if not model_path.exists():

        print("[ERROR] Local model is missing.")

        return {
            "scenario": "missing_model_artifact",
            "expected": "RECOVER",
            "actual": "NOT_TESTED",
            "passed": False
        }

    backup_path = Path(
        str(model_path) + ".lab10_backup"
    )

    shutil.copy2(model_path, backup_path)

    os.remove(model_path)

    try:

        # Step 1: Detect missing model

        print("[INFO] Checking missing model detection...")

        failure_exit_code = run_script(
            "src/mlops_pipeline/06_model_evaluation.py"
        )

        failure_detected = failure_exit_code != 0

        # Step 2: Configure MLflow

        configure_mlflow(config)

        # Step 3: Load registered model version 4
        # Version 4 was registered using Pickle serialization.

        model_uri = f"models:/{model_name}/4"

        print(
            f"[INFO] Recovering model from {model_uri}..."
        )

        production_model = mlflow.sklearn.load_model(
            model_uri
        )

        # Step 4: Restore local model

        model_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        joblib.dump(
            production_model,
            model_path
        )

        print(
            "[SUCCESS] Model recovered from MLflow."
        )

        # Step 5: Evaluate recovered model

        print(
            "[INFO] Evaluating recovered model..."
        )

        recovery_exit_code = run_script(
            "src/mlops_pipeline/06_model_evaluation.py"
        )

        recovered = recovery_exit_code == 0

        passed = failure_detected and recovered

        return {
            "scenario": "missing_model_artifact",
            "expected": "RECOVER",
            "actual": (
                "RECOVERED"
                if passed
                else "RECOVERY_FAILED"
            ),
            "failure_detected": failure_detected,
            "recovery_succeeded": recovered,
            "passed": passed
        }

    finally:

        # Restore the original local model
        restore_file(
            backup_path,
            model_path
        )


# ==========================================================
# MAIN EXECUTION
# ==========================================================

def run_failure_tests():

    print("[INFO] ================================================")

    print(
        "[INFO] Lab 10 Failure Handling and Recovery"
    )

    print("[INFO] ================================================")

    config_path = PROJECT_ROOT / "config.yaml"

    with open(
        config_path,
        "r",
        encoding="utf-8"
    ) as file:

        config = yaml.safe_load(file)

    repetitions = int(
        config["lab9"]["repetitions"]
    )

    all_runs = []

    tests = [
        test_missing_data,
        test_invalid_datatype,
        test_schema_mismatch,
        test_preprocessing_inconsistency,
        test_missing_model_with_recovery
    ]

    for repetition in range(
        1,
        repetitions + 1
    ):

        print("\n" + "=" * 70)

        print(
            f"[INFO] Lab 10 Repetition "
            f"{repetition}/{repetitions}"
        )

        print("=" * 70)

        repetition_results = []

        for test in tests:

            result = test(config)

            repetition_results.append(result)

            print(
                "[RESULT]",
                result["scenario"],
                "PASSED" if result["passed"] else "FAILED"
            )

        all_runs.append(
            {
                "repetition": repetition,
                "results": repetition_results,
                "passed": all(
                    item["passed"]
                    for item in repetition_results
                )
            }
        )

    # Generate final report

    report = {
        "stage": "Lab 10 Failure Handling and Recovery",
        "repetitions": repetitions,
        "runs": all_runs,
        "overall_status": (
            "PASSED"
            if all(
                run["passed"]
                for run in all_runs
            )
            else "FAILED"
        )
    }

    report_path = (
        PROJECT_ROOT / config["paths"]["failure_report"]
    )

    report_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4
        )

    # Display final result

    if report["overall_status"] == "PASSED":

        print(
            "\n[SUCCESS] All Lab 10 scenarios PASSED."
        )

        print(
            f"[INFO] Report saved to {report_path}"
        )

        return True

    print(
        "\n[ERROR] One or more Lab 10 scenarios FAILED."
    )

    print(
        f"[INFO] Report saved to {report_path}"
    )

    return False


if __name__ == "__main__":

    passed = run_failure_tests()

    sys.exit(
        0 if passed else 1
    )