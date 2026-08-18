FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app/apps/front-end
COPY apps/front-end/requirements.txt /tmp/frontend-requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install -r /tmp/frontend-requirements.txt

COPY apps/front-end/ ./

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]