# MLflow and CI Setup

## Objective
To integrate MLflow experiment tracking and GitHub Actions CI into the MLOps project.

## Setup
1. Install dependencies from `requirements.txt`.
2. Activate the Python virtual environment.
3. Run the Lab 4 tracking pipeline.
4. Configure GitHub Actions using `.github/workflows/lab8_ci.yml`.
5. Check workflow execution in the GitHub Actions tab.

## Commands

```bash
pip install -r requirements.txt
python pipelines/run_lab4_tracking.py
```

## Result
MLflow is used for experiment tracking, and GitHub Actions automates pipeline execution. Verify successful execution in MLflow and GitHub Actions.