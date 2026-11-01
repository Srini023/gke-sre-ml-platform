Days 1 and 2: Setup and First GKE Cluster
Nov 1, 2026 · @Srinivas BV
Day 1: setup and foundations
Day 1 produced a clean public repo, working tools, and a GCP project with cost controls in place.
• Repo: created the public repo Srini023/gke-sre-ml-platform with a folder layout for the 11 weeks, a .gitignore that blocks secrets and Terraform state, and a README.
• Git identity: set your name and a private GitHub email, and fixed a 403 push error caused by wrong token permissions.
• Tools: confirmed gcloud, kubectl, the GKE auth plugin, Terraform, Helm, Docker and k6 work in WSL. kind was skipped so Kubernetes is learned directly on GKE.
• GCP: logged in, set the project, confirmed billing is on, and enabled the GKE, Compute, Artifact Registry and IAM APIs.
• Cost control: found the ₹28,796 free-trial credit, which expires on 8 Jan 2027. Changed the budget (₹5,100, alerts at 50%, 75% and 100%) so it tracks spend before credits.
• Documentation: wrote the setup log and the Day 1 README.
Day 2: Terraform and the first GKE cluster
Day 2 built a repeatable, low-cost way to create and destroy a real GKE cluster, and it was destroyed cleanly the same night.
• Remote state: created a versioned GCS bucket for Terraform state, kept outside Terraform so terraform destroy never deletes it.
• Infrastructure as code: wrote Terraform for a VPC and subnet, a least-privilege node service account, a zonal GKE Standard cluster with workload identity, and a Spot node pool of two small nodes.
• Create and destroy: applied it, confirmed the cluster ran in the console, then destroyed it and checked that no clusters, instances or disks were left.
• Documentation: committed the code and wrote notes on remote state, node pools and workload identity.
What it shows
You can now create and destroy a real GKE cluster on demand, with secrets and spend under control. That is the base for Kubernetes practice, observability and LLM serving in the coming weeks, and it makes a good interview story.
