# Day 3 notes: pods, deployments, probes, rollouts

## Troubleshooting: x509 certificate signed by unknown authority

### Symptom
After recreating the GKE cluster, every kubectl command failed:

    Unable to connect to the server: tls: failed to verify certificate:
    x509: certificate signed by unknown authority

### Context
- Day 2: created cluster `sre-ml-gke`, ran `get-credentials`, then destroyed it.
- Day 3: ran `terraform apply` and got a new cluster with the same name.
- I ran `kubectl get nodes` without refreshing credentials first.

### Root cause
Every GKE cluster generates its own certificate authority (CA). `get-credentials`
stores the cluster endpoint and CA certificate in `~/.kube/config`. My kubeconfig
still held the CA of the cluster I destroyed on Day 2. The new API server's
certificate was signed by a different CA, so kubectl could not verify it and
correctly refused to connect. The cluster name and context name were identical,
which hid the problem. The endpoint IP can also change on recreate.

### How to confirm the diagnosis
1. Check which cluster kubectl is targeting:

       kubectl config current-context
       kubectl config view --minify

2. Compare the CA in kubeconfig with the CA the cluster really has. The two
   hashes differ when the entry is stale:

       kubectl config view --minify --raw \
         -o jsonpath='{.clusters[0].cluster.certificate-authority-data}' \
         | tr -d '\n' | md5sum
       gcloud container clusters describe sre-ml-gke --zone asia-south1-a \
         --format='value(masterAuth.clusterCaCertificate)' | tr -d '\n' | md5sum

3. Check the endpoint matches too:

       gcloud container clusters describe sre-ml-gke --zone asia-south1-a \
         --format='value(endpoint)'



### Fix
Refresh the kubeconfig entry. It overwrites the old endpoint and CA:

    gcloud container clusters get-credentials sre-ml-gke \
      --zone asia-south1-a --project srevert-sri023
    kubectl get nodes

If an old entry lingers, delete it first:

    kubectl config delete-context gke_srevert-sri023_asia-south1-a_sre-ml-gke
    kubectl config delete-cluster gke_srevert-sri023_asia-south1-a_sre-ml-gke

### What slowed me down
- I ran `(terraform output -raw get_credentials)` without the leading `$`, so the
  shell printed the command instead of running it. The refresh never happened.
  Lesson: after a fix, check the output for "kubeconfig entry generated".
- A second paste had `kubectlkubectl`. Long pastes into the terminal can drop or
  join characters. Paste small blocks and read them before pressing Enter.

### Prevention
- Run `get-credentials` as the first command after every `terraform apply`.
- After `terraform destroy`, delete the stale context and cluster entries.
- Never use `--insecure-skip-tls-verify`. It hides the error and removes the
  protection against talking to the wrong server.

### Interview summary (30 seconds)
"kubectl failed with an x509 unknown authority error after I recreated a GKE
cluster with the same name. Each cluster has its own CA, and my kubeconfig still
had the old one, so TLS verification failed. I confirmed it by comparing the CA
in kubeconfig with the cluster's CA, refreshed credentials with gcloud, and added
a rule to run get-credentials after every apply."

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
