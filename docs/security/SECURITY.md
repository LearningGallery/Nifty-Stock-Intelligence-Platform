# Security Overview

## Security Controls
- Cognito authentication
- IAM least privilege
- Private S3 buckets
- Encryption at rest and in transit
- WAF for rate limiting and managed protections
- CloudWatch logging
- Secrets Manager for API keys

## Secret Handling
- Never hardcode secrets in code
- Store API keys in Secrets Manager
- Use environment variables only for non-sensitive config

## API Protection
- WAF rate limiting
- JWT validation
- CORS restrictions
- input validation and sanitization

## Document Access Boundaries
- Uploaded documents tagged by user_id
- Access checked before returning status or deleting files
- Production enhancement: stronger row-level authorization

## Logging Considerations
- Do not log secrets
- Avoid logging raw tokens
- Avoid storing sensitive uploaded document content in logs

## Production Hardening Recommendations
- Replace self-signed ALB cert with ACM-managed cert
- Enable CloudTrail organization-wide
- Add GuardDuty and Security Hub
- Use KMS CMKs for stricter encryption control
- Add malware scanning for uploaded files
