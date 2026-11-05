# GKE SRE ML Platform

Reliable ML and LLM serving on Google Kubernetes Engine: Terraform, GitOps (ArgoCD),
observability, SLOs, autoscaling and canary releases.

Work in progress. Built day by day as part of a structured SRE upskilling plan.

## What works today

- GKE Standard cluster (zonal, Spot nodes, Dataplane V2) created and destroyed with Terraform, state in a versioned GCS bucket
- FastAPI iris classifier with health and readiness endpoints, tests, and a non-root container image in Artifact Registry
- Deployed to GKE with plain manifests and with a Helm chart (upgrade, atomic rollback, uninstall)
- ConfigMap, Secret, Ingress and NetworkPolicy labs, with notes on what failed and why
- `gke-guard`: a Python cost guard that warns when a cluster is left running

Every lab session ends with `terraform destroy`, so nothing keeps billing.

## Layout

| Folder | Purpose |
|---|---|
| `infra/gcp` | Terraform for GKE, IAM, networking and remote state |
| `k8s` | Kubernetes manifests and Helm charts |
| `observability` | Prometheus, Grafana, Loki, OpenTelemetry and SLO configs |
| `pipelines` | CI/CD and ML pipelines |
| `app` | Sample model server (FastAPI, iris) |
| `llm-serving` | vLLM on GKE: metrics, load tests, autoscaling |
| `runbooks` | Incident runbooks and postmortems |
| `tools` | Small Python SRE tools, for example `gke-guard`, a cost guard for clusters left running |
| `docs` | Charter, notes and architecture |

## Roadmap

1. Kubernetes fundamentals on GKE
2. GKE with Terraform and ArgoCD
3. Observability and SLOs
4. LLM serving with vLLM
5. CI/CD and supply-chain security
6. Autoscaling and canary rollback
7. Chaos testing and postmortems
8. EU compliance notes (GDPR, data residency)

Planned next: drift monitoring and FinOps.

## Daily log

| Day | Topic | Notes |
|---|---|---|
| 1 | Repo, tools, GCP project, budget | `docs/day1-setup-log.md`, `docs/day1-readme.md` |
| 2 | Terraform remote state, first GKE cluster | `docs/day2-notes.md`, `infra/gcp/` |
| 3 | Pods, deployments, probes, rollouts | `docs/day3-notes.md`, `k8s/day3/` |
| 4 | ConfigMaps, Secrets, Ingress, NetworkPolicy | `docs/day4-notes.md`, `k8s/day4/` |
| 5 | Iris FastAPI container, Artifact Registry, GKE deploy | `docs/day5-notes.md`, `app/`, `k8s/day5/` |
| 6 | Helm chart, upgrade, atomic rollback, uninstall; gke-guard tool | `docs/day6-notes.md`, `k8s/helm/iris-api/`, `tools/gke-guard/` |
| 7 | Week 1 wrap-up: README refresh, log parser, pytest tests | `docs/day7-notes.md`, `tools/log-parser/`, `tools/gke-guard/` |
