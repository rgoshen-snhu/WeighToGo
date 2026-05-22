"""FastAPI application for the Weigh to Go! backend."""

from fastapi import FastAPI

from weighttogo.config import get_settings

app = FastAPI(title="Weigh to Go! API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Report service liveness and the active environment."""
    return {"status": "ok", "environment": get_settings().environment}
