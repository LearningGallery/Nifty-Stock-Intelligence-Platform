#!/usr/bin/env bash
set -euo pipefail

cd backend
docker build -t nsip-backend:latest .

cd ../frontend
docker build -t nsip-frontend:latest .
```

## `scripts/init-terraform.sh`
```bash
#!/usr/bin/env bash
set -euo pipefail

cd terraform
terraform fmt -recursive
terraform init
terraform validate
