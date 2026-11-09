# Day 8: iris on GKE, rollout failure and rollback

## What I did
- Repo audit: gitleaks clean (18 commits). Added .pytest_cache to .gitignore.
- Created EU Artifact Registry (europe-west3/iris), pushed iris-api:16a7c17 (tag = git SHA).
- GKE Standard zonal cluster sre-lab, 1 x e2-standard-2 spot node, europe-west3-a.
- Deployed the iris Helm chart (k8s/helm/iris-api) into namespace iris.
- Verified /healthz, /readyz, /predict (setosa), and 422 on invalid input.
- Drills: bad image upgrade -> helm rollback -> helm upgrade --atomic.
- Destroyed the cluster at the end of the session.

## Evidence
- Revision 2: helm said "deployed" while the new pod was ErrImagePull.
- Rolling update with 2 replicas: maxSurge 1, maxUnavailable 0, so old pods stayed and the rollout stalled safely.
- Rollback to 1 reused ReplicaSet 5858f7bdc9: same pods, no restart.
- --atomic --timeout 60s: revision 4 failed, revision 5 auto-rollback to 3.

## Answers
1. Why did /healthz keep answering during the bad rollout?
   -
2. helm rollback vs kubectl rollout undo: why not mix them?
   -
3. Why does rollback create a new revision?
   -
4. Why tag images with a commit SHA, not latest?
   -

## Interview line
"Plain helm upgrade reports success on a broken release; in CI we use --atomic."

## Decision
Skipped kind. Working directly on short-lived GKE sessions, destroyed after each one.
