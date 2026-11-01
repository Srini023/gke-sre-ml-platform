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
