from fastapi.testclient import TestClient

from main import app

GOOD = {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}


def test_health_and_ready():
    with TestClient(app) as c:
        assert c.get("/healthz").json() == {"status": "ok"}
        assert c.get("/readyz").json() == {"ready": True}


def test_predict_setosa():
    with TestClient(app) as c:
        r = c.post("/predict", json=GOOD)
        assert r.status_code == 200
        assert r.json() == {"species": "setosa"}


def test_rejects_negative_value():
    with TestClient(app) as c:
        r = c.post("/predict", json={**GOOD, "sepal_length": -1})
        assert r.status_code == 422


def test_metrics_endpoint_counts_predictions():
    from fastapi.testclient import TestClient
    from main import app

    with TestClient(app) as client:
        client.post("/predict", json={"sepal_length": 5.1, "sepal_width": 3.5,
                                      "petal_length": 1.4, "petal_width": 0.2})
        body = client.get("/metrics").text
    assert 'http_requests_total{method="POST",route="/predict",status="200"}' in body
    assert 'iris_predictions_total{species="setosa"}' in body
