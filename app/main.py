"""Iris classifier API with Prometheus metrics."""
import os
import random
import time
from contextlib import asynccontextmanager

import joblib
from fastapi import FastAPI, HTTPException, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field

state = {}

# RED metrics. Label by route TEMPLATE, never the raw URL: raw URLs make
# unbounded label values (high cardinality) and can take Prometheus down.
HTTP_REQUESTS = Counter(
    "http_requests_total", "HTTP requests", ["method", "route", "status"]
)
HTTP_LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP request latency in seconds",
    ["method", "route"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.15, 0.2, 0.25, 0.5, 1.0, 2.5),
)
PREDICTIONS = Counter("iris_predictions_total", "Predictions by species", ["species"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    state.update(joblib.load("model.joblib"))
    yield
    state.clear()


app = FastAPI(title="iris-api", lifespan=lifespan)


@app.middleware("http")
async def record_metrics(request: Request, call_next):
    start = time.perf_counter()
    status = 500  # if the handler raises, count it as a server error
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        route = request.scope.get("route")
        path = route.path if route else "unmatched"
        if path != "/metrics":  # don't measure the scrapes themselves
            HTTP_LATENCY.labels(request.method, path).observe(time.perf_counter() - start)
            HTTP_REQUESTS.labels(request.method, path, str(status)).inc()


class IrisFeatures(BaseModel):
    sepal_length: float = Field(gt=0, lt=20)
    sepal_width: float = Field(gt=0, lt=20)
    petal_length: float = Field(gt=0, lt=20)
    petal_width: float = Field(gt=0, lt=20)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    return {"ready": "model" in state}


@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/predict")
def predict(f: IrisFeatures):
    # Fault injection for SLO/alert drills. Both default to 0 = off.
    latency_ms = int(os.getenv("FAULT_LATENCY_MS", "0"))
    if latency_ms > 0:
        time.sleep(latency_ms / 1000)
    if random.random() < float(os.getenv("FAULT_ERROR_RATE", "0")):
        raise HTTPException(status_code=503, detail="injected fault")
    row = [[f.sepal_length, f.sepal_width, f.petal_length, f.petal_width]]
    idx = int(state["model"].predict(row)[0])
    species = state["classes"][idx]
    PREDICTIONS.labels(species).inc()
    return {"species": species}
