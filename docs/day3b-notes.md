
## Concepts
- Pod: smallest unit, one or more containers sharing an IP. Deployment owns a
  ReplicaSet; the ReplicaSet keeps the desired number of pods alive.
- Service: stable virtual IP and DNS name that load-balances to ready pods by
  label, because pod IPs change whenever pods are recreated.
- Readiness probe: failing removes the pod from Service endpoints (no traffic).
  Liveness probe: failing makes the kubelet restart the container.
- requests: what the scheduler reserves when choosing a node. limits: ceiling
  enforced at runtime. Over the memory limit = OOMKilled; over the CPU limit =
  throttled.
- maxSurge 1: up to one pod above the desired count during a rollout.
  maxUnavailable 0: ready pods never drop below the desired count.

## Lab results
- Self-healing: deleted all 3 pods, the ReplicaSet recreated them in about a second.
- Pods start `Running` but `0/1` until the readiness probe passes.
- Scale 3 to 5 and back: pods spread over both nodes, roughly balanced.
- Good rollout (1.27 to 1.28): one new pod, wait for ready, remove one old pod,
  repeat. A new ReplicaSet was created and the old one kept at 0 for rollback.
- Bad image (nginx:1.99.99): new pod ErrImagePull then ImagePullBackOff, event says
  not found. Old pods kept serving because maxUnavailable is 0.
- Bad probe (path /nope): container Running, READY 0/1, RESTARTS 0, event
  "Readiness probe failed: statuscode 404". No traffic, no restarts.
- `kubectl rollout undo` restored the last good ReplicaSet each time.

## Failure patterns
| Symptom | Container running? | Cause | First check |
|---|---|---|---|
| ImagePullBackOff | no | bad tag or registry access | describe pod, events |
| Running, 0/1 | yes | readiness probe failing | events, app logs |
| CrashLoopBackOff | restarts | app crashes or liveness fails | logs --previous |

## Drift and change-cause
- `kubectl set image` and `rollout undo` change the cluster but not my YAML or the
  last-applied annotation, so Git said 1.27 while the cluster ran 1.28. This is
  why GitOps (ArgoCD, Week 2) makes Git the source of truth.
- CHANGE-CAUSE is copied from an annotation at each revision, so it was wrong for the
  bad-image revision. It must be updated with every change.

## Network errors seen
- x509 unknown authority: stale kubeconfig (see above).
- dial tcp ... i/o timeout: brief network issue reaching the public control plane;
  a retry worked. Timeout = network path, x509 = trust.
