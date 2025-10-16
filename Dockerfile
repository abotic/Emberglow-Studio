FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    nodejs \
    npm \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz \
    && tar -xf ffmpeg-master-latest-linux64-gpl.tar.xz \
    && mv ffmpeg-master-latest-linux64-gpl/bin/* /usr/local/bin/ \
    && rm -rf ffmpeg-master-latest-linux64-gpl*

WORKDIR /app

COPY . .

RUN pip install -r backend/requirements.txt
RUN cd frontend && npm install && npm run build

WORKDIR /app/backend

ENTRYPOINT ["python", "app.py"]