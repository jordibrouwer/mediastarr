FROM python:3.12-slim

LABEL org.opencontainers.image.title="Mediastarr"
LABEL org.opencontainers.image.description="Independent automated media search for Sonarr & Radarr. Not affiliated with Huntarr."
LABEL org.opencontainers.image.version="4.0"

WORKDIR /app

RUN pip install --no-cache-dir flask requests gunicorn

COPY app/       ./app/
COPY templates/ ./templates/
COPY static/    ./static/

VOLUME ["/data"]
EXPOSE 7979

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7979/api/state')" || exit 1

ENV DATA_DIR=/data          \
    SONARR_URL=""           \
    SONARR_API_KEY=""       \
    RADARR_URL=""           \
    RADARR_API_KEY=""       \
    HUNT_MISSING_DELAY=900  \
    HUNT_UPGRADE_DELAY=1800 \
    MAX_SEARCHES_PER_RUN=10 \
    DAILY_LIMIT=20          \
    COOLDOWN_DAYS=7         \
    DRY_RUN=false           \
    AUTO_START=true         \
    LANGUAGE=de

CMD ["python", "app/main.py"]
