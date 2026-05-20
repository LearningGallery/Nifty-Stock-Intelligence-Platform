# Disaster Recovery

## Recovery Objectives
- RTO: 2 hours
- RPO: 24 hours

## Backups
- DynamoDB PITR
- OpenSearch snapshots
- S3 versioning
- Terraform state versioning

## Recovery Steps
1. restore infra/state
2. restore DynamoDB tables if needed
3. restore OpenSearch snapshot
4. redeploy backend/frontend
5. validate health and core use cases
