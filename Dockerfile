FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV WAKEWORD_NAME=hey_jarvis
ENV WAKEWORD_THRESHOLD=0.6
ENV WAKEWORD_MODEL_PATH=/root/.cache/openwakeword/models/hey_jarvis_v0.1.tflite

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    portaudio19-dev \
    libasound2-dev \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip setuptools wheel
RUN pip install -r /app/requirements.txt

RUN python -c "import openwakeword; openwakeword.utils.download_models()"

COPY . /app

CMD ["python", "-u", "main.py"]