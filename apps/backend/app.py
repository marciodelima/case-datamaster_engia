from fastapi import FastAPI

from backend.dataconnector.models import BackendHealth

app = FastAPI(title="Data Master Backend", version="0.1.0")


@app.get("/health", response_model=BackendHealth)
def health() -> BackendHealth:
    return BackendHealth(service="backend")


@app.get("/ready", response_model=BackendHealth)
def ready() -> BackendHealth:
    return BackendHealth(service="backend")
