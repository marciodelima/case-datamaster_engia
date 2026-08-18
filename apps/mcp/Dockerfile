FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/apps

WORKDIR /app/apps
COPY apps/requirements.txt /tmp/service-requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install -r /tmp/service-requirements.txt

COPY apps/mcp/ ./service/
COPY apps/agents/ ./agents/
RUN touch service/__init__.py

EXPOSE 8101
CMD ["uvicorn", "service.app:app", "--host", "0.0.0.0", "--port", "8101"]