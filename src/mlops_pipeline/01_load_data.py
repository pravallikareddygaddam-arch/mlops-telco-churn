
import os
import sys
import json
import shutil
from datetime import datetime

import pandas as pd
import yaml


def load_data():
    print("[INFO] Starting Data Loading...")

    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    data_path = config["data"]["raw_path"]
    new_data_path = "data/raw/new_churn.csv"
    archive_path = "data/processed/ingested_new_churn.csv"

    os.makedirs("artifacts", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    # Check whether new data is available
    if os.path.exists(new_data_path):

        print("[INFO] New dataset detected.")

        df = pd.read_csv(new_data_path)

        if df.empty:
            print("[ERROR] New dataset is empty.")
            return False

        required_columns = [
            config["data"]["id_column"],
            config["data"]["target_column"]
        ]

        missing = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing:
            print(f"[ERROR] Missing required columns: {missing}")
            return False

        # Back up the existing dataset before replacing it
        if os.path.exists(data_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"data/raw/churn_backup_{timestamp}.csv"

            shutil.copy2(data_path, backup_path)
            print(f"[INFO] Original dataset backed up to: {backup_path}")

        # Replace the configured raw dataset with the new dataset
        shutil.copy2(new_data_path, data_path)

        # Archive the incoming dataset to prevent repeated ingestion
        if os.path.exists(archive_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_path = (
                f"data/processed/ingested_new_churn_{timestamp}.csv"
            )

        shutil.move(new_data_path, archive_path)

        status = "ingested"
        source_file = archive_path

        print("[SUCCESS] New dataset ingested successfully.")

    else:
        print("[INFO] No new dataset found.")

        if not os.path.exists(data_path):
            print(f"[ERROR] Raw dataset not found: {data_path}")
            return False

        df = pd.read_csv(data_path)

        if df.empty:
            print("[ERROR] Existing dataset is empty.")
            return False

        status = "no_new_data"
        source_file = data_path

    print(
        f"[INFO] Loaded {df.shape[0]} rows, "
        f"{df.shape[1]} columns."
    )

    report = {
        "stage": "ML Pipeline - Data Loading",
        "status": status,
        "source_file": source_file,
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": df.columns.tolist(),
        "dtypes": df.dtypes.astype(str).to_dict()
    }

    with open(
        "artifacts/data_load_report.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(report, f, indent=4)

    print("[SUCCESS] Data loading report saved.")
    print(f"[INFO] Status: {status}")

    return True


if __name__ == "__main__":
    passed = load_data()
    sys.exit(0 if passed else 1)
