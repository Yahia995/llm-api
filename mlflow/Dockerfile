FROM python:3.10-slim

WORKDIR /mlflow

RUN pip install --no-cache-dir mlflow psycopg2-binary

EXPOSE 5000

CMD mlflow server \
    --host 0.0.0.0 \
    --port 5000 \
    --backend-store-uri ${DATABASE_URL} \
    --default-artifact-root /mlflow/artifacts \
    --serve-artifacts \
    --allowed-hosts '*'
