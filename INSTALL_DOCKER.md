# Installation von marker mit Docker

## Voraussetzungen

- Docker installiert: https://www.docker.com/get-started/

## Dockerfile Beispiel

```dockerfile
FROM python:3.12-slim

# System-Abhängigkeiten
RUN apt-get update && apt-get install -y git build-essential && rm -rf /var/lib/apt/lists/*

# marker klonen
RUN git clone https://github.com/VikParuchuri/marker.git /app
WORKDIR /app

# Python-Abhängigkeiten
RUN pip install --upgrade pip
RUN pip install -e .
RUN pip install torch streamlit watchdog

# Port für Streamlit
EXPOSE 8501

# Startbefehl
CMD ["streamlit", "run", "marker/scripts/streamlit_app.py", "--server.headless=true", "--server.port=8501", "--server.address=0.0.0.0"]
```

## Build und Start

```bash
docker build -t marker-app .
docker run -p 8501:8501 marker-app
```

Die Streamlit-GUI ist dann unter http://localhost:8501 erreichbar.