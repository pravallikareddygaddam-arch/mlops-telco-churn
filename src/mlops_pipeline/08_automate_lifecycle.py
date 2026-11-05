
import os
import sys
import json
import yaml
import mlflow

from pathlib import Path
from datetime import datetime, timezone
from mlflow.tracking import MlflowClient


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config.yaml"


def automate_model_lifecycle():

    print("[INFO] Starting Automated Model Lifecycle Manager...")

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    tracking_uri = (
        os.getenv("MLFLOW_TRACKING_URI")
        or config["mlflow"].get("tracking_uri")
    )

    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)

    client = MlflowClient()

    model_name = config["registry"]["model_name"]
    metric_name = config["registry"]["decision_metric"]

    report_path = PROJECT_ROOT / "reports" / "lifecycle_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "status": "started",
        "model_name": model_name,
        "decision_metric": metric_name,
        "candidate_version": None,
        "candidate_run_id": None,
        "candidate_metric": None,
        "production_version_before": None,
        "production_metric_before": None,
        "promoted": False,
        "decision": "NO_DECISION",
        "production_version_after": None,
        "reason": "",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    try:
        # 1. Read registered model versions.
        all_versions = client.search_model_versions(
            f"name='{model_name}'"
        )

        print(f"[INFO] Model: {model_name}")
        print(f"[INFO] Metric: {metric_name}")

        # 2. Identify the current Production model.
        production_models = [
            mv for mv in all_versions
            if mv.current_stage == "Production"
        ]

        production_model = (
            max(production_models, key=lambda x: int(x.version))
            if production_models else None
        )

        if production_model:
            production_run = client.get_run(production_model.run_id)

            production_score = production_run.data.metrics.get(
                metric_name
            )

            report["production_version_before"] = int(
                production_model.version
            )
            report["production_metric_before"] = production_score

            print(
                f"[INFO] Production Version {production_model.version} "
                f"| {metric_name}={production_score}"
            )

        # 3. Move new candidate versions to Staging.
        for mv in all_versions:

            if mv.current_stage == "None":

                client.transition_model_version_stage(
                    name=model_name,
                    version=mv.version,
                    stage="Staging",
                    archive_existing_versions=False
                )

                print(
                    f"[INFO] Version {mv.version} moved to Staging."
                )

        # 4. Get Staging models.
        all_versions = client.search_model_versions(
            f"name='{model_name}'"
        )

        staging_models = [
            mv for mv in all_versions
            if mv.current_stage == "Staging"
        ]

        if not staging_models:

            report["status"] = "success"
            report["decision"] = "NO_CANDIDATE"
            report["reason"] = "No models available in Staging."

            report["production_version_after"] = (
                int(production_model.version)
                if production_model else None
            )

            print("[INFO] No models available in Staging.")

            return True

        # 5. Select the best candidate.
        best_model = None
        best_score = float("-inf")

        for mv in staging_models:

            run = client.get_run(mv.run_id)

            score = run.data.metrics.get(metric_name)

            if score is None:
                print(
                    f"[WARNING] Version {mv.version} "
                    f"does not contain {metric_name}. Skipping."
                )
                continue

            print(
                f"[INFO] Staging Version {mv.version} "
                f"| {metric_name}={score:.4f}"
            )

            if score > best_score:
                best_score = score
                best_model = mv

        if best_model is None:

            for mv in staging_models:
                client.transition_model_version_stage(
                    name=model_name,
                    version=mv.version,
                    stage="Archived",
                    archive_existing_versions=False
                )

            report["status"] = "success"
            report["decision"] = "NO_VALID_CANDIDATE"
            report["reason"] = (
                f"No staging model has the metric {metric_name}."
            )

            report["production_version_after"] = (
                int(production_model.version)
                if production_model else None
            )

            return True

        report["candidate_version"] = int(best_model.version)
        report["candidate_run_id"] = best_model.run_id
        report["candidate_metric"] = float(best_score)

        # 6. Compare candidate against Production.
        if production_model is None or report[
            "production_metric_before"
        ] is None:

            promote = True

        else:

            promote = (
                best_score > report["production_metric_before"]
            )

        # 7. Promote or archive the candidate.
        if promote:

            client.transition_model_version_stage(
                name=model_name,
                version=best_model.version,
                stage="Production",
                archive_existing_versions=True
            )

            report["promoted"] = True
            report["decision"] = "PROMOTED"
            report["reason"] = (
                "Candidate model passed the production comparison."
            )

            print(
                f"[SUCCESS] Version {best_model.version} "
                "promoted to Production."
            )

        else:

            client.transition_model_version_stage(
                name=model_name,
                version=best_model.version,
                stage="Archived",
                archive_existing_versions=False
            )

            report["promoted"] = False
            report["decision"] = "ARCHIVED"
            report["reason"] = (
                "Candidate did not improve the production metric."
            )

            print(
                f"[INFO] Version {best_model.version} archived."
            )

        # 8. Archive remaining staging versions.
        final_versions = client.search_model_versions(
            f"name='{model_name}'"
        )

        for mv in final_versions:

            if mv.current_stage == "Staging":

                client.transition_model_version_stage(
                    name=model_name,
                    version=mv.version,
                    stage="Archived",
                    archive_existing_versions=False
                )

        # 9. Read final Production version.
        final_versions = client.search_model_versions(
            f"name='{model_name}'"
        )

        final_production = [
            mv for mv in final_versions
            if mv.current_stage == "Production"
        ]

        if final_production:
            report["production_version_after"] = int(
                final_production[0].version
            )

        report["status"] = "success"

        print("[SUCCESS] Model lifecycle completed.")

        return True

    except Exception as exc:

        report["status"] = "failed"
        report["decision"] = "ERROR"
        report["reason"] = str(exc)

        print("[ERROR]", exc)

        return False

    finally:

        report["timestamp"] = datetime.now(
            timezone.utc
        ).isoformat()

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)

        print(
            f"[INFO] Lifecycle report saved: {report_path}"
        )


if __name__ == "__main__":
    success = automate_model_lifecycle()
    sys.exit(0 if success else 1)

