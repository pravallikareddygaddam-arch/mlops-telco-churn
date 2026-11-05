
import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

LIFECYCLE_REPORT = PROJECT_ROOT / "reports" / "lifecycle_report.json"

PREPARE_SCRIPT = (
    PROJECT_ROOT / "src" / "mlops_pipeline" / "11_prepare_deployment.py"
)

DEPLOY_SCRIPT = PROJECT_ROOT / "deployment" / "deploy_production.py"


def load_lifecycle_report():
    if not LIFECYCLE_REPORT.exists():
        raise FileNotFoundError(
            f"Lifecycle report not found: {LIFECYCLE_REPORT}"
        )

    with LIFECYCLE_REPORT.open("r", encoding="utf-8") as file:
        return json.load(file)


def run_script(script_path):
    if not script_path.exists():
        print(f"[ERROR] Script not found: {script_path}")
        return False

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=PROJECT_ROOT
    )

    return result.returncode == 0


def main():
    print("=" * 70)
    print("DEPLOY IF MODEL WAS PROMOTED")
    print("=" * 70)

    try:
        report = load_lifecycle_report()

        # 1. Validate lifecycle report.
        if report.get("status") != "success":
            print("[ERROR] Lifecycle report is not successful.")
            print("[INFO] Deployment skipped.")
            return False

        model_name = report.get("model_name")
        promoted = report.get("promoted", False)
        candidate_version = report.get("candidate_version")
        production_version = report.get("production_version_after")

        print(f"[INFO] Model name        : {model_name}")
        print(f"[INFO] Candidate version : {candidate_version}")
        print(f"[INFO] Promoted          : {promoted}")
        print(f"[INFO] Production version: {production_version}")

        # 2. Check promotion decision.
        if not promoted:
            print("[INFO] Candidate was not promoted.")
            print("[INFO] Production deployment skipped.")
            return True

        if candidate_version is None:
            print("[ERROR] Candidate version is missing.")
            return False

        if production_version != candidate_version:
            print("[ERROR] Production version does not match candidate.")
            print("[INFO] Deployment skipped.")
            return False

        # 3. Prepare deployment artifacts.
        print("[INFO] Preparing deployment artifacts...")

        if not run_script(PREPARE_SCRIPT):
            print("[ERROR] Deployment preparation failed.")
            return False

        print("[SUCCESS] Deployment artifacts prepared.")

        # 4. Deploy production model.
        print("[INFO] Starting production deployment...")

        if not run_script(DEPLOY_SCRIPT):
            print("[ERROR] Production deployment failed.")
            return False

        print("[SUCCESS] Production deployment completed.")

        return True

    except Exception as exc:
        print(f"[ERROR] Deployment process failed: {exc}")
        return False


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
