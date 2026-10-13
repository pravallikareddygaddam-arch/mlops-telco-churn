# Lab 8 – Continuous Integration Report

## Objective
To implement Continuous Integration for the Churn Prediction MLOps pipeline using GitHub Actions.

## Workflow
File: `.github/workflows/lab8_ci.yml`

Triggers:
- Push to `main` or `master`
- Pull requests
- Manual workflow dispatch

## CI Environment
- Ubuntu latest
- Python 3.11
- GitHub Actions checkout and Python setup
- Dependencies installed from `requirements.txt`

## Execution
The workflow runs:

```bash
python src/mlops_pipeline/churn_prediction_pipeline.py
```

## Result
The CI workflow is configured to automate pipeline execution. Successful completion must be confirmed from the GitHub Actions run.