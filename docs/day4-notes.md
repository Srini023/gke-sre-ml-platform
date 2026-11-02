# Day 4 notes: ConfigMaps, Secrets, Ingress, NetworkPolicy

## Setup change
NetworkPolicy is only enforced if the cluster supports it. I enabled Dataplane V2
in Terraform (`datapath_provider = "ADVANCED_DATAPATH"`) and confirmed it with
`gcloud container clusters describe ... networkConfig.datapathProvider`.

## ConfigMaps and Secrets
- Applied the Deployment before its Secret existed: pods went to
  `CreateContainerConfigError` (RESTARTS 0), event `secret "db-credentials" not found`.
  The image had pulled fine. After `kubectl create secret` the pods recovered on
  their own.
- A Secret is base64, not encryption: `base64 -d` returned the value. Never commit
  Secret YAML. Real setups add KMS encryption at rest, RBAC and a secret manager.
- Edited the ConfigMap: the mounted file updated in the running pod without a
  restart, but the env var stayed `sandbox` until `kubectl rollout restart`.
  Env vars are fixed at container start. A rotated Secret used as an env var has
  the same problem. Mounts with `subPath` do not update at all.

## Ingress
- GKE Ingress created a Google load balancer. Status codes went 000, then 404,
  then 200, about 8 minutes after apply. Do not debug in the first minutes.
- The Ingress creates resources Terraform does not know about (forwarding rule,
  URL map, backend service, NEGs, health check, firewall rules). Delete the
  Ingress first, confirm those lists are empty, then `terraform destroy`.

## NetworkPolicy
- Before any policy, every pod could reach `app`.
- `default-deny-ingress` (podSelector {}) plus `allow-from-clients` (role=client):
  the labelled pod got the page, the unlabelled pod got `download timed out`
  (a silent drop, not a refusal).
- Finding: right after default-deny the Ingress went from 200 to 502 although the
  pods were healthy. Adding `allow-from-load-balancer` for 130.211.0.0/22 and
  35.191.0.0/16 (the source ranges in Google's GKE Ingress docs) brought 200
  back. Cause is inferred from before/after behaviour, not from a log line.
  Lesson: map traffic sources before rolling out default-deny.
- Labelling the unlabelled pod `role=client` opened access with no policy change,
  but the first request still timed out and the same request worked about 10
  seconds later. Policy changes take seconds to apply, so wait and recheck before
  concluding a rule failed. Anyone who can set pod labels can open a path, which
  RBAC has to protect.

## Debugging cheat sheet
| Message | Meaning |
|---|---|
| `CreateContainerConfigError` | container cannot be created: missing Secret or ConfigMap, or bad key |
| `wget: bad address` | DNS lookup failed: typo, wrong namespace, or missing Service |
| `download timed out` | name resolved but packets dropped: policy, firewall or dead pod |
| Ingress 000, then 404, then 200 | load balancer still being programmed |
| Ingress 502 | backend unhealthy or blocked from the load balancer |

## Minor findings
- `get-credentials` warned about an invalid kubeconfig after I deleted the last
  context, cluster and user. gcloud backed it up and recreated it. Harmless.
- The `grep -A8 "Events:"` on describe output printed nothing twice; cause unknown.
  `kubectl get events --sort-by=.lastTimestamp` is reliable.
- Replaced pasted tokens with `gh auth login` (token stored in plain text in
  ~/.config/gh, outside the repo).
