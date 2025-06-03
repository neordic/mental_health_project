FROM python:3.11-slim

WORKDIR /app

COPY ./ml_inference/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./ml_inference ./ml_inference
COPY ./ml_service ./ml_service
COPY ./tests ./tests


ENV PYTHONPATH="/app"

WORKDIR /app

CMD ["celery", "-A", "ml_inference.core.celery_app", "worker", "--loglevel=info"]

