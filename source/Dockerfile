FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg libsm6 libxext6 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./celery_worker/ /app/celery_worker/
COPY ./download_image_from_minio/ /app/download_image_from_minio
COPY ./inference/ /app/inference/
COPY ./logger/ /app/logger/
COPY ./minio/ /app/minio/
COPY ./prepare_data_services/ /app/prepare_data_services/
COPY ./processing_raw_image/ /app/processing_raw_image
COPY ./utils.py /app/utils.py