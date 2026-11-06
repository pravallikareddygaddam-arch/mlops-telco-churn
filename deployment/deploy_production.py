
import json
import subprocess
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEPLOYMENT_DIR = PROJECT_ROOT / "deployment"
METADATA_PATH = DEPLOYMENT_DIR / "model_metadata.json"
K8S_DEPLOYMENT_PATH = PROJECT_ROOT / "k8s" / "deployment.yaml"
REPORT_PATH = PROJECT_ROOT / "reports" / "deployment_automation_report.json"

IMAGE_NAME = "churn-prediction-api"


def run_command(command):
    print(f"[INFO] Running: {' '.join(command)}")
    return subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )


def load_metadata():
    with METADATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_report(report):
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_PATH.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)


def deploy_production():
    print("=" * 60)
    print("PRODUCTION DEPLOYMENT")
    print("=" * 60)

    metadata = load_metadata()

    if metadata.get("model_stage") != "Production":
        raise RuntimeError("Deployment blocked: model is not in Production stage.")

    model_version = metadata["model_version"]
    model_path = DEPLOYMENT_DIR / "model.pkl"
    preprocessor_path = DEPLOYMENT_DIR / "preprocessor.pkl"

    if not model_path.exists() or not preprocessor_path.exists():
        raise FileNotFoundError("Model or preprocessor artifact is missing.")

    image_tag = f"{IMAGE_NAME}:model-v{model_version}"

    # Build or reuse Docker image
    check = run_command(["docker", "image", "inspect", image_tag])

    if check.returncode == 0:
        print("[INFO] Docker image already exists. Reusing it.")
    else:
        print("[INFO] Building Docker image...")
        result = run_command(["docker", "build", "-t", image_tag, "."])
        if result.returncode != 0:
            raise RuntimeError(result.stderr or "Docker build failed.")

    # Kubernetes is optional when no cluster is available
    k8s_status = "skipped"
    deployment_name = None
    container_name = None
    app_label = None

    if K8S_DEPLOYMENT_PATH.exists():
        with K8S_DEPLOYMENT_PATH.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        deployment_name = config["metadata"]["name"]
        app_label = config["metadata"]["labels"]["app"]
        container_name = config["spec"]["template"]["spec"]["containers"][0]["name"]

        cluster = run_command(["kubectl", "cluster-info"])

        if cluster.returncode == 0:
            existing = run_command([
                "kubectl", "get", "deployment", deployment_name
            ])

            if existing.returncode == 0:
                update = run_command([
                    "kubectl", "set", "image",
                    f"deployment/{deployment_name}",
                    f"{container_name}={image_tag}"
                ])

                if update.returncode != 0:
                    raise RuntimeError(update.stderr or "Kubernetes image update failed.")

                rollout = run_command([
                    "kubectl", "rollout", "status",
                    f"deployment/{deployment_name}",
                    "--timeout=120s"
                ])

                if rollout.returncode != 0:
                    raise RuntimeError(rollout.stderr or "Kubernetes rollout failed.")

                k8s_status = "success"
            else:
                print("[WARNING] Kubernetes deployment not found. Skipping update.")
        else:
            print("[WARNING] Kubernetes cluster unavailable. Skipping Kubernetes update.")
    else:
        print("[WARNING] Kubernetes deployment YAML not found. Skipping update.")

    report = {
        "status": "success",
        "model_name": metadata["model_name"],
        "model_version": str(model_version),
        "run_id": metadata.get("run_id"),
        "docker_image": image_tag,
        "docker_status": "success",
        "kubernetes_status": k8s_status,
        "kubernetes_context": "docker-desktop",
        "kubernetes_deployment": deployment_name,
        "kubernetes_container": container_name,
        "app_label": app_label,
        "deployment_bundle": {
            "model": str(model_path.relative_to(PROJECT_ROOT)),
            "preprocessor": str(preprocessor_path.relative_to(PROJECT_ROOT)),
            "metadata": str(METADATA_PATH.relative_to(PROJECT_ROOT))
        }
    }

    save_report(report)

    print("[SUCCESS] Docker deployment image is ready.")
    print(f"[INFO] Kubernetes status: {k8s_status}")
    print(f"[SUCCESS] Deployment report saved: {REPORT_PATH}")

    return True


if __name__ == "__main__":
    try:
        sys.exit(0 if deploy_production() else 1)
    except Exception as exc:
        print(f"[ERROR] Production deployment failed: {exc}")
        sys.exit(1)
