#!/usr/bin/env bash
set -euo pipefail

echo "==> Deploying infrastructure"
cd terraform
terraform init
terraform plan -out=tfplan
terraform apply -auto-approve tfplan

echo "==> Building backend"
cd ../backend
docker build -t nsip-backend:latest .

echo "==> Building frontend"
cd ../frontend
npm install
npm run build

echo "Deployment steps completed. Continue with image push and S3 sync."
