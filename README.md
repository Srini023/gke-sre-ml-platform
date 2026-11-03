# GKE SRE ML Platform

Reliable ML and LLM serving on Google Kubernetes Engine: Terraform, GitOps (ArgoCD),
observability, SLOs, autoscaling and canary releases.

Work in progress. Built day by day as part of a structured SRE upskilling plan.

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
| `docs` | Charter, notes and architecture |

## Roadmap

1. Kubernetes fundamentals on kind
2. GKE with Terraform and ArgoCD
3. Observability and SLOs
4. LLM serving with vLLM
5. CI/CD and supply-chain security
6. Autoscaling and canary rollback
7. Chaos testing and postmortems
8. EU compliance notes (GDPR, data residency)

Planned next: CKA-level depth, drift monitoring, FinOps.

## Daily log

| Day | Topic | Notes |
|---|---|---|
| 1 | Repo, tools, GCP project, budget | `docs/day1-setup-log.md`, `docs/day1-readme.md` |
| 2 | Terraform remote state, first GKE cluster | `docs/day2-notes.md`, `infra/gcp/` |
| 3 | Pods, deployments, probes, rollouts | `docs/day3-notes.md`, `k8s/day3/` |
| 4 | ConfigMaps, Secrets, Ingress, NetworkPolicy | `docs/day4-notes.md`, `k8s/day4/` |
| 5 | Iris FastAPI container, Artifact Registry, GKE deploy | `docs/day5-notes.md`, `app/`, `k8s/day5/` |
