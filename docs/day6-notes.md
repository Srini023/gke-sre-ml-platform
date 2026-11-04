# Day 6: Helm chart for the iris API

## What I built
- Helm chart `k8s/helm/iris-api/` (Chart.yaml, values.yaml, templates/deployment.yaml, templates/service.yaml). Same Deployment and Service as Day 5, with replicas, image tag, ports and resources moved into values.yaml.
- Checked it without a cluster: `helm lint` and `helm template` (with `--set` overrides).
- Python extra: `tools/gke-guard/gke_guard.py`, which warns if a GKE cluster is left running. Uses subprocess, json, logging and exit codes (0 none, 1 found, 2 could not check).

## Helm lifecycle on GKE (release `iris-api`, namespace `day6`)
| Revision | Action | Result |
|---|---|---|
| 1 | `helm upgrade --install` | deployed, 2 pods |
| 2 | `--set replicaCount=3` | 3 pods; only 1 new pod, old pods untouched |
| 3 | `--set image.tag=does-not-exist --atomic --timeout 60s` | failed, auto rollback |
| 4 | automatic rollback | "Rollback to 2" |
| 5 | `helm rollback iris-api 1` | "Rollback to 1", back to 2 pods |
- `helm uninstall` removed Deployment, Pods and Service in one command.

## Observations
- A failed upgrade does not take the app down: the rolling update keeps old pods serving while new pods wait for readiness. `--atomic` then restores the release.
- Rollback creates a NEW revision. History is never rewritten.
- `helm template` renders YAML locally with no cluster, which is useful for review and CI.
- toYaml prints keys sorted alphabetically (limits before requests); harmless.
- gke-guard: a bad project gives exit code 2 with a one-line error; error text from gcloud includes the account email, so do not paste it publicly.

## Interview points
- Helm vs raw YAML: templating, versioned releases, one-command rollback and uninstall.
- What does --atomic do, and what does the history look like afterwards?
- Why is a bad image tag not an outage (readiness gating plus rolling update)?
- upgrade --install is idempotent, so it suits CI/CD.
- Why scripts return meaningful exit codes (CI and schedulers act on them).
