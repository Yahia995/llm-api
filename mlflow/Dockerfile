FROM python:3.10-slim

WORKDIR /mlflow

RUN pip install mlflow

EXPOSE 5000

CMD mlflow server \
    --host 0.0.0.0 \
    --port 5000 \
    --backend-store-uri sqlite:///mlflow/mlflow.db \
    --default-artifact-root /mlflow/mlruns \
    --serve-artifacts \
    --allowed-hosts '*'