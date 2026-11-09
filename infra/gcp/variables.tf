variable "project_id" {
  type    = string
  default = "srevert-sri023"
}

variable "region" {
  type    = string
  default = "europe-west3"
}

variable "zone" {
  type    = string
  default = "europe-west3-a"
}

variable "cluster_name" {
  type    = string
  default = "sre-ml-gke"
}

variable "node_count" {
  type    = number
  default = 1
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
