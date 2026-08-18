FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/apps

WORKDIR /app/apps
COPY apps/requirements.txt /tmp/service-requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install -r /tmp/service-requirements.txt

COPY apps/backend/ ./backend/

EXPOSE 8000
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]