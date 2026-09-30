\# Lab 8 – Continuous Integration Report



\## Objective



Implement Continuous Integration for the Churn Prediction MLOps pipeline using GitHub Actions.



\## Workflow



The CI workflow is located at:



.github/workflows/lab8\_ci.yml



The workflow is configured to run for:



\- Pushes to main

\- Pushes to master

\- Pull requests

\- Manual workflow dispatch



\## CI Environment



The workflow uses:



\- Ubuntu latest runner

\- Python 3.11

\- Repository checkout using actions/checkout

\- Python setup using actions/setup-python

\- Dependencies installed from requirements.txt



\## Pipeline Execution



The CI workflow executes:



```powershell

python src/mlops\_pipeline/churn\_prediction\_pipeline.py

