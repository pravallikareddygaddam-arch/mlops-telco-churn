
import numpy as np
import pandas as pd

from pathlib import Path
from scipy.stats import ks_2samp


# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

BASELINE_PATH = PROJECT_ROOT / "data/processed/X_test_raw.csv"
EVOLVED_PATH = PROJECT_ROOT / "data/monitoring/drift/evolved_data.csv"
REPORT_PATH = PROJECT_ROOT / "outputs/drift/data_drift_report.csv"


NUMERICAL_COLUMNS = [
    "MonthlyCharges",
    "tenure",
    "TotalCharges"
]

CATEGORICAL_COLUMNS = [
    "Contract",
    "InternetService",
    "PaymentMethod"
]

KS_THRESHOLD = 0.10
JS_THRESHOLD = 0.10


def load_data():

    if not BASELINE_PATH.exists():
        raise FileNotFoundError(
            f"Baseline dataset not found: {BASELINE_PATH}"
        )

    if not EVOLVED_PATH.exists():
        raise FileNotFoundError(
            f"Evolved dataset not found: {EVOLVED_PATH}"
        )

    baseline = pd.read_csv(BASELINE_PATH)
    evolved = pd.read_csv(EVOLVED_PATH)

    required_columns = (
        NUMERICAL_COLUMNS + CATEGORICAL_COLUMNS
    )

    for column in required_columns:

        if column not in baseline.columns:
            raise ValueError(
                f"Column {column} missing in baseline dataset"
            )

        if column not in evolved.columns:
            raise ValueError(
                f"Column {column} missing in evolved dataset"
            )

    if baseline.empty or evolved.empty:
        raise ValueError("One of the datasets is empty.")

    return baseline, evolved


def calculate_js_divergence(baseline, evolved):

    baseline = baseline.dropna().astype(str)
    evolved = evolved.dropna().astype(str)

    categories = sorted(
        set(baseline.unique()) |
        set(evolved.unique())
    )

    if not categories:
        return 0.0

    baseline_counts = (
        baseline.value_counts(normalize=True)
        .reindex(categories, fill_value=0)
        .to_numpy(dtype=float)
    )

    evolved_counts = (
        evolved.value_counts(normalize=True)
        .reindex(categories, fill_value=0)
        .to_numpy(dtype=float)
    )

    midpoint = (baseline_counts + evolved_counts) / 2

    baseline_mask = baseline_counts > 0
    evolved_mask = evolved_counts > 0

    kl_baseline = np.sum(
        baseline_counts[baseline_mask] *
        np.log2(
            baseline_counts[baseline_mask] /
            midpoint[baseline_mask]
        )
    )

    kl_evolved = np.sum(
        evolved_counts[evolved_mask] *
        np.log2(
            evolved_counts[evolved_mask] /
            midpoint[evolved_mask]
        )
    )

    return float((kl_baseline + kl_evolved) / 2)


def analyze_numerical_drift(baseline, evolved):

    results = []

    for column in NUMERICAL_COLUMNS:

        baseline_values = pd.to_numeric(
            baseline[column],
            errors="coerce"
        ).dropna()

        evolved_values = pd.to_numeric(
            evolved[column],
            errors="coerce"
        ).dropna()

        if baseline_values.empty or evolved_values.empty:
            raise ValueError(
                f"Insufficient numerical data in {column}"
            )

        statistic, p_value = ks_2samp(
            baseline_values,
            evolved_values
        )

        status = (
            "DRIFT"
            if statistic >= KS_THRESHOLD
            else "OK"
        )

        results.append({
            "feature": column,
            "type": "numerical",
            "metric": "KS",
            "score": round(float(statistic), 6),
            "p_value": round(float(p_value), 6),
            "threshold": KS_THRESHOLD,
            "status": status
        })

    return results


def analyze_categorical_drift(baseline, evolved):

    results = []

    for column in CATEGORICAL_COLUMNS:

        score = calculate_js_divergence(
            baseline[column],
            evolved[column]
        )

        status = (
            "DRIFT"
            if score >= JS_THRESHOLD
            else "OK"
        )

        results.append({
            "feature": column,
            "type": "categorical",
            "metric": "JS",
            "score": round(score, 6),
            "p_value": None,
            "threshold": JS_THRESHOLD,
            "status": status
        })

    return results


def create_drift_report(baseline, evolved):

    results = []

    results.extend(
        analyze_numerical_drift(baseline, evolved)
    )

    results.extend(
        analyze_categorical_drift(baseline, evolved)
    )

    report = pd.DataFrame(results)

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    report.to_csv(
        REPORT_PATH,
        index=False
    )

    return report


def print_report(report):

    print("\n" + "=" * 70)
    print("LAB 12 - DATA DRIFT ANALYSIS")
    print("=" * 70)

    print("\nBaseline dataset:", BASELINE_PATH)
    print("Evolved dataset :", EVOLVED_PATH)

    print("\nDrift Results:\n")
    print(report.to_string(index=False))

    drift_count = (
        report["status"] == "DRIFT"
    ).sum()

    total_features = len(report)

    print("\n" + "=" * 70)
    print("Features analyzed :", total_features)
    print("Drift detected    :", drift_count)
    print("Report saved      :", REPORT_PATH)
    print("=" * 70)


def main():

    baseline, evolved = load_data()

    print("[INFO] Baseline shape:", baseline.shape)
    print("[INFO] Evolved shape :", evolved.shape)

    report = create_drift_report(
        baseline,
        evolved
    )

    print_report(report)

    print("\n[SUCCESS] Lab 12 Data Drift Analysis Completed!")


if __name__ == "__main__":

    try:
        main()

    except Exception as error:
        print("\n[ERROR]", error)
        raise
