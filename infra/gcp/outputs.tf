output "cluster_name" {
  value = google_container_cluster.primary.name
}

output "get_credentials" {
  value = "gcloud container clusters get-credentials ${var.cluster_name} --zone ${var.zone} --project ${var.project_id}"
}
