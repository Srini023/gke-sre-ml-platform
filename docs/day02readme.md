Day 2 has three parts: remote state, the Terraform files, then create, use and destroy a small GKE cluster. Paste one block at a time, as we did on Day 1. Plan about 2.5 to 3 hours.

Before you start (5 minutes)

Check Google’s GKE pricing page for asia-south1. As far as I know, a zonal cluster carries a management fee that a monthly free-tier credit may cover, but I haven’t verified that, so read it yourself. The nodes bill separately, which is why we use small Spot nodes and destroy everything at the end.

Block 1: state bucket (one-time)

Terraform can’t store its state in a bucket that doesn’t exist yet, so create this one with gcloud. It stays outside Terraform, so terraform destroy never deletes it.

gcloud storage buckets create gs://srevert-sri023-tfstate \
  --location=asia-south1 --uniform-bucket-level-access
gcloud storage buckets update gs://srevert-sri023-tfstate --versioning
gcloud storage buckets list

Block 2: write the Terraform files

Work in ~/projects/gke-sre-ml-platform/infra/gcp. Paste each file separately, then cat it.

versions.tf
cd ~/projects/gke-sre-ml-platform/infra/gcp
cat > versions.tf <<'EOF'
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }

  backend "gcs" {
    bucket = "srevert-sri023-tfstate"
    prefix = "infra/gcp"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}
EOF


variables.tf

cat > variables.tf <<'EOF'
variable "project_id" {
  type    = string
  default = "srevert-sri023"
}

variable "region" {
  type    = string
  default = "asia-south1"
}

variable "zone" {
  type    = string
  default = "asia-south1-a"
}

variable "cluster_name" {
  type    = string
  default = "sre-ml-gke"
}

variable "node_count" {
  type    = number
  default = 2
}

variable "machine_type" {
  type    = string
  default = "e2-standard-2"
}

variable "use_spot" {
  description = "Spot nodes are cheaper but can be reclaimed at any time"
  type        = bool
  default     = true
}
EOF

network.tf
cat > network.tf <<'EOF'
resource "google_compute_network" "vpc" {
  name                    = "${var.cluster_name}-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = "${var.cluster_name}-subnet"
  region        = var.region
  network       = google_compute_network.vpc.id
  ip_cidr_range = "10.10.0.0/20"
}
EOF

gke.tf
cat > gke.tf <<'EOF'
resource "google_service_account" "nodes" {
  account_id   = "gke-nodes"
  display_name = "GKE node service account"
}

resource "google_project_iam_member" "node_roles" {
  for_each = toset([
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/monitoring.viewer",
    "roles/artifactregistry.reader",
  ])
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.nodes.email}"
}

resource "google_container_cluster" "primary" {
  name                = var.cluster_name
  location            = var.zone
  network             = google_compute_network.vpc.id
  subnetwork          = google_compute_subnetwork.subnet.id
  deletion_protection = false

  remove_default_node_pool = true
  initial_node_count       = 1

  release_channel {
    channel = "REGULAR"
  }

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  ip_allocation_policy {}

  resource_labels = {
    env     = "sandbox"
    project = "gke-sre-ml-platform"
  }
}

resource "google_container_node_pool" "primary_nodes" {
  name       = "primary-pool"
  cluster    = google_container_cluster.primary.name
  location   = var.zone
  node_count = var.node_count

  node_config {
    machine_type    = var.machine_type
    spot            = var.use_spot
    disk_size_gb    = 50
    disk_type       = "pd-balanced"
    service_account = google_service_account.nodes.email
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]

    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    labels = {
      env = "sandbox"
    }
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  depends_on = [google_project_iam_member.node_roles]
}
EOF

outputs.tf
cat > outputs.tf <<'EOF'
output "cluster_name" {
  value = google_container_cluster.primary.name
}

output "get_credentials" {
  value = "gcloud container clusters get-credentials ${var.cluster_name} --zone ${var.zone} --project ${var.project_id}"
}
EOF
ls

Block 3: init, check, plan
terraform init
terraform fmt
terraform validate
terraform plan

init should say it configured the gcs backend. The plan should show about 9 resources to add: the VPC, subnet, service account, four IAM bindings, the cluster and the node pool. Paste the plan summary line, and any error, before applying. A quota error on CPUs or disks would show up here or at apply time. If it does, paste it and we’ll adjust the machine type or node count.

Block 4: apply, connect, test   terraform apply

terraform apply

$(terraform output -raw get_credentials)
kubectl get nodes
kubectl get pods -A
kubectl create deployment hello --image=nginx --replicas=2
kubectl get pods -o wide
kubectl delete deployment hello

You should see 2 nodes in Ready state and system pods in kube-system. Take a look at the cluster in the console under Kubernetes Engine → Clusters, and note what you see.

Block 5: destroy

Always do this at the end of the session:

terraform destroy
gcloud container clusters list
gcloud compute instances list

Both lists should come back empty.


Block 6: commit
cd ~/projects/gke-sre-ml-platform
git status

git status should show the .tf files and .terraform.lock.hcl, and not .terraform/ or any .tfstate file. If it matches:
git status should show the .tf files and .terraform.lock.hcl, and not .terraform/ or any .tfstate file. If it matches:
git add infra/gcp
git commit -m "day2: terraform remote state and zonal GKE cluster"
git push

git add infra/gcp
git commit -m "day2: terraform remote state and zonal GKE cluster"
git push

Day 2 checklist
 State bucket created with versioning
 terraform init, validate and plan clean
 Cluster created, 2 nodes Ready, test deployment ran
 terraform destroy run, lists empty
 Committed and pushed
 Short note in docs/ on what you learned (2 to 3 lines per concept: remote state, node pool, workload identity)

If you get stuck, tell me which block and paste the output. If it takes you longer than expected, stop after the plan and do the apply tomorrow. Don’t leave a cluster running overnight.
