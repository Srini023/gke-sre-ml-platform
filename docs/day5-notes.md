# Day 5: Iris API container, Artifact Registry, GKE deploy

## What I built
- FastAPI iris classifier (`app/`): `/healthz` (liveness), `/readyz` (model loaded), `/predict` with pydantic validation (negative values return 422).
- 3 pytest tests, all pass. Use `with TestClient(app)` so the lifespan loads the model.
- Dockerfile: python:3.12-slim, pinned requirements, model trained inside the image (same scikit-learn version as serving), non-root user uid 10001. Image 594MB on disk, 138MB compressed.
- Artifact Registry repo `iris` in asia-south1; image pushed as `iris-api:0.1`. Digest matched the local image ID.
- GKE: Deployment (2 replicas, probes, requests 100m/128Mi, limits 500m/512Mi, runAsNonRoot) + ClusterIP Service in namespace `day5`.

## Observations
- Pods spread across both nodes. Memory about 102Mi each (limit 512Mi).
- Delete BOTH pods: 4 failures in 60 requests (about 4s of `Connection refused`; Service had no ready endpoints).
- Delete ONE pod: 0 failures in 60 requests. The replacement stayed 0/1 until /readyz passed and got no traffic until then.
- Takeaway: replicas plus a readiness probe make losing one pod invisible; losing all is an outage.

## Problems and fixes
- `python` not found: venv was not active (only `python3` exists outside a venv).
- `python3 -m venv` failed on ensurepip: `sudo apt install python3.12-venv`, remove the half-built `.venv`, retry.
- Tests that ran too early returned empty/000 twice (docker run and port-forward): `sleep 3` is a race. Use a retry loop on /readyz.
- Git push asked for a password: the Day 1 cache helper (8h) expired. Fixed permanently: removed it and ran `gh auth setup-git`.
- My delete test first matched both pods (label selector) and then used `delete pod` with `-o name`, which already includes `pod/`. Always check the output actually shows what you meant to delete.

## Interview points
- Liveness vs readiness, and why /readyz checks the model.
- Why train in the image build (version pinning), non-root, layer caching.
- Single vs multiple replica failure test with numbers.
