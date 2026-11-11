# Day 9: GKE from Terraform, NetworkPolicy, Workload Identity, ArgoCD GitOps

## Built
- terraform apply of infra/gcp: 9 resources (VPC, subnet, node SA, 4 IAM, cluster, node pool) in 11m37s.
- Verified: Dataplane V2 (anetd), Workload Identity pool, node SA gke-nodes@, spot node, GKE_METADATA.
- iris via `helm upgrade --install --atomic`; image pull proved the Terraform IAM binding.
- terraform destroy: 9 destroyed in 9m18s; nothing left (clusters, VPC, disks, LBs, firewall).

## NetworkPolicy (k8s/day9/networkpolicy.yaml)
- Default-deny ingress + allow app=iris from role=client on port 8000.
- No label: wget timed out. role=client: {"status":"ok"}.
- Policy port is the POD port (8000), not the Service port (80).
- Pods stayed 1/1 under default-deny: kubelet probes are node-local and allowed.

## Workload Identity (k8s/day9/workload-identity.yaml)
- KSA iris/reader -> GSA wi-reader (roles/iam.workloadIdentityUser), GSA has objectViewer on the bucket.
- Pod with reader SA: identity wi-reader@, read object, HTTP 200. Default SA: HTTP 403.
- First attempt failed silently: IAM propagation delay of a minute or two.

## ArgoCD GitOps (k8s/argocd/iris-app.yaml)
- Found values.yaml still pointed at the deleted asia-south1 image: --set had hidden it. Fixed in git.
- Synced/Healthy 7 s after creation; same ReplicaSet hash 5858f7bdc9 as Helm CLI.
- Self-heal: manual scale to 5 reverted in ~2 s.
- Git change: replicaCount 3 (14d5b4e) applied; rollback = git revert (f7e5fca).
- Pods ending in Error 30 s after Terminating: tested clean delete = 3.5 s, so not a SIGTERM bug;
  startup race when pods are deleted while still starting.

## Interview lines
- remove_default_node_pool: GKE must create a pool; separate pool resource lets me change
  machine type/spot/GPU without recreating the cluster. Costs ~4 min per build.
- Terraform owns infrastructure; Helm/ArgoCD own workloads. One owner per object.
- LoadBalancer Services create GCP resources outside Terraform; delete them before terraform destroy.
- GitOps: git is the source of truth, self-heal reverts drift, rollback is git revert.
- Production: private nodes + Cloud NAT, pinned ArgoCD version, deletion_protection = true.
