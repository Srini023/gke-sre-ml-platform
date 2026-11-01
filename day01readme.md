# Day 1: Setup log and actions taken

Date: 1 November 2026
Project: `srevert-sri023` | Region: `asia-south1` | Zone: `asia-south1-a`

Goal of Day 1: a clean public repo, working tools, a verified GCP project with cost controls, and nothing running that costs money.

## 1. Repository

| Action | Result |
|---|---|
| Decided to start a new repo instead of reusing the old one | Clean history, and the repo sits under the same account as the CV link |
| Created public repo `Srini023/gke-sre-ml-platform` (no README, .gitignore or license) | Empty repo on GitHub |
| Cloned it to `~/projects/gke-sre-ml-platform` in WSL | Local working copy |
| Created folders: `infra/gcp`, `k8s`, `observability`, `pipelines`, `runbooks`, `docs`, `app`, `llm-serving` (each with `.gitkeep`) | Skeleton for the 11-week plan |
| Added `.gitignore` (Terraform state, `.tfvars`, `.env`, key files, kubeconfig, Python and editor files) | Prevents secrets and state from being committed |
| Added `README.md` with layout table and roadmap | Project overview |
| First commit and push to `main` | Skeleton live on GitHub |

## 2. Git identity and access

- Set `user.name` to `Srinivas B V`.
- Turned on "Keep my email addresses private" on GitHub and set `user.email` to the GitHub noreply address, so the real email is not exposed in commits.
- Pushing returned HTTP 403. Cause: the fine-grained personal access token had no repository selected and the wrong permission (Actions instead of Contents).
- Fix: limited the token to this one repository with **Contents: Read and write**, removed the Actions permission, and retried. Push succeeded.
- Cached credentials for 8 hours (`credential.helper cache`), so the token is held in memory only.

## 3. Tools verified in WSL (Ubuntu)

| Tool | Version |
|---|---|
| Google Cloud SDK (gcloud) | 588.0.0 |
| kubectl (client) | v1.35.9 |
| gke-gcloud-auth-plugin | installed |
| Terraform | v1.16.5 |
| Helm | v3.22.0 |
| Docker | 29.1.3 (daemon reachable from WSL) |
| k6 | v2.3.0 |

Decision: skip `kind` and learn Kubernetes directly on GKE. Rule: create, work and `terraform destroy` in each session.

## 4. GCP setup

| Action | Result |
|---|---|
| `gcloud auth login` | Failed once with a scope-changed error (consent screen returned fewer permissions). Fixed by revoking, logging in again and ticking every permission box |
| `gcloud auth application-default login` | Application Default Credentials saved (used by Terraform) |
| Set ADC quota project to `srevert-sri023` | Removed the quota-project warning |
| Set active project to `srevert-sri023` | Confirmed in `gcloud config list` |
| Checked billing | `billingEnabled: True`, billing account open |
| Inventoried existing resources | No service accounts and no buckets, so nothing to destroy or clean up |
| Reviewed the existing budget `COSTCONTROL` | Monthly INR budget with alerts at 50%, 75% and 100% |
| Enabled APIs | `container`, `compute`, `artifactregistry`, `iam`, `cloudresourcemanager` (Logging and Monitoring were already on) |
| Set defaults | Region `asia-south1`, zone `asia-south1-a` |

## 5. Documentation

- Wrote `docs/day1-setup-log.md` with tool versions and the GCP baseline.
- Committed and pushed it (`day1: setup log with tool versions and GCP baseline`).

## 6. Findings and open items

- The account has a **free-trial credit**. The existing budget counts spend *after* credits, so its alerts will not fire until the credit is used up. To do: change the budget to track spend before credits, lower the target amount, and confirm an email recipient is set.
- To do: note the credit's expiry date and whether the account is still a free-trial account. Free-trial accounts can have restrictions (for example on GPUs), so confirm before the GPU work in Week 4.
- To do: keep a private list of real metrics from the current role (incidents per month, MTTR, scale, deployment frequency) for the CV rewrite on 7 November.

## 7. Lessons learned

- Long multi-line pastes can get garbled in the terminal. Paste in smaller blocks and `cat` each file before committing.
- A 403 on push after a successful login usually means token permissions, not the password.
- Always check the credits and budget settings before creating billable resources.

## Day 1 checklist

- [x] Repo created, skeleton pushed
- [x] Git identity set, email kept private
- [x] Tools installed and verified
- [x] GCP login, project and billing confirmed
- [x] Budget exists
- [x] APIs enabled, default region and zone set
- [x] Setup log committed
- [ ] Budget changed to track spend before credits, recipient confirmed
- [ ] Credit expiry and account type noted
- [ ] CV metrics list started

## Next: Day 2 (2 November)

Terraform remote state on GCS, then a small zonal GKE Standard cluster. Create it, connect with `kubectl`, run a first pod, then destroy it the same session.

