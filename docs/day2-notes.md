# Day 2 notes: Terraform state, node pools, workload identity

## Remote state
Terraform keeps a state file that maps my code to the real resources it created.
I store it in a GCS bucket with versioning on, so it is not lost with my laptop,
can be shared, and is locked while someone runs apply. The bucket was created by
hand with gcloud, outside Terraform, so `terraform destroy` never deletes it.

## Node pool
The control plane is managed by Google. The nodes that run my pods are VMs
grouped in a node pool with one shared config (machine type, disk, service
account, Spot or on-demand). I delete the default pool and define my own so I
control cost and security. Spot nodes are cheaper but can be reclaimed at any
time, which is fine for a sandbox. Auto-repair and auto-upgrade keep nodes healthy.

## Workload identity
It lets a pod call Google APIs as a Google service account, through a Kubernetes
service account, with no key files. It is enabled with the workload pool
`PROJECT.svc.id.goog` on the cluster and the GKE metadata mode on the nodes. The
nodes themselves use a dedicated low-privilege service account (logging,
monitoring and image pull only) instead of the default Compute Engine account.

## Habit
Create, work, `terraform destroy`, then check `gcloud container clusters list`
is empty. A running cluster costs money.
