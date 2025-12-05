FROM ghcr.io/coqui-ai/tts

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git wget curl ffmpeg libsndfile1 pkg-config \
    libavcodec-dev libavformat-dev libavdevice-dev libavutil-dev \
    libavfilter-dev libswscale-dev libswresample-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt /root/requirements.txt
RUN pip install --upgrade pip
RUN pip install av==12.0.0 --only-binary=:all:
RUN pip install -r /root/requirements.txt huggingface_hub

# Set working directory
WORKDIR /app

# Copy project
COPY . /app

# Copy and run model setup scripts
COPY docker-scripts/download_eg_model.py /root/download_eg_model.py
COPY docker-scripts/register_model.py /root/register_model.py

RUN python3 /root/download_eg_model.py
RUN python3 /root/register_model.py

# Expose port
EXPOSE 8080

# Start FastAPI app on Cloud Run expected port
CMD ["uvicorn", "ar_voice_assistant.main:app", "--host", "0.0.0.0", "--port", "8080"]
