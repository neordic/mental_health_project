FROM python:3.11-slim

WORKDIR /app


RUN apt-get update && \
    apt-get install -y curl bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


COPY ./ml_service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


COPY ./ml_service ./ml_service
COPY ./ml_inference ./ml_inference

ENV PYTHONPATH="/app"

WORKDIR /app/ml_service

CMD ["bash", "-c", "python init_db.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]