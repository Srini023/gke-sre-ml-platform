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
