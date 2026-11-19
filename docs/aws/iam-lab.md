# AWS IAM lab (Day 12)

Identity: console sign-in = assumed-role/AccountFullAccessRole (STS temporary credentials).

## Findings
- Created role sre-lab-s3-reader: trust policy (account principal) + AmazonS3ReadOnlyAccess.
- sts:AssumeRole blocked: explicit deny in an Organizations SCP, even for a full-access role.
- simulate-principal-policy (includes SCPs):
  s3:ListAllMyBuckets allowed; s3:GetObject and s3:CreateBucket explicitDeny
  (AllowedByOrganizations=False); iam:ListRoles implicitDeny.
- simulate-custom-policy (policy only): Allow s3:* + Deny s3:DeleteBucket ->
  GetObject/PutObject allowed, DeleteBucket explicitDeny, ec2:DescribeInstances implicitDeny.

## Rules
Default deny. Explicit deny always wins. SCPs and boundaries limit, never grant.
Cross-account needs both sides. Trust policy = who; permissions policy = what.

## GCP comparison
GCP binds roles to principals on resources, inherited down org/folder/project.
AWS attaches policies to identities or resources, per account.
Service account ~ IAM role; Workload Identity ~ IRSA / EKS Pod Identity.
