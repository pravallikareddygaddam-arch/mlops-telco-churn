FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# requirements-api.txt is not present in the project root, so install only
# the runtime packages required by the FastAPI inference service.
RUN pip install --no-cache-dir \
    fastapi==0.141.1 \
    "uvicorn[standard]==0.52.4" \
    pydantic==2.13.4 \
    numpy==2.4.6 \
    pandas==2.3.3 \
    scikit-learn==1.9.0 \
    joblib==1.5.3 \
    PyYAML==6.0.3

COPY api/ ./api/
COPY deployment/ ./deployment/
COPY config.yaml ./config.yaml

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
