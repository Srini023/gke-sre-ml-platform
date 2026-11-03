"""Iris classifier API."""
from contextlib import asynccontextmanager

import joblib
from fastapi import FastAPI
from pydantic import BaseModel, Field

state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    state.update(joblib.load("model.joblib"))
    yield
    state.clear()


app = FastAPI(title="iris-api", lifespan=lifespan)


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


@app.post("/predict")
def predict(f: IrisFeatures):
    row = [[f.sepal_length, f.sepal_width, f.petal_length, f.petal_width]]
    idx = int(state["model"].predict(row)[0])
    return {"species": state["classes"][idx]}
