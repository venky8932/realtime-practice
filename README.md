# Kubernetes Deployment Setup

This repository contains a minimal deployment for:
- API service (Python)
- Web service (Node.js)
- Python worker service
- RDS PostgreSQL connection from the API service
- HTTP communication between the web service and the API service
- Kubernetes Deployments + ClusterIP Services
- Horizontal Pod Autoscalers for API and web services
- Secrets for DB credentials
- Basic alert watcher sending email when all replicas fail
- Health check scheduler every 5 minutes for API and web services

## Folder structure

- `fastapi/`
  - `main.py`
  - `requirements.txt`
  - `Dockerfile`
- `nodejs/`
  - `app.js`
  - `package.json`
  - `Dockerfile`
- `worker/`
  - `worker.py`
  - `Dockerfile`
- `alert-watcher/`
  - `watcher.py`
  - `requirements.txt`
  - `Dockerfile`
- `k8s/`
  - `secret-db.yaml`
  - `fastapi-deployment.yaml`
  - `fastapi-service.yaml`
  - `nodejs-deployment.yaml`
  - `nodejs-service.yaml`
  - `worker-deployment.yaml`
  - `worker-service.yaml`
  - `fastapi-hpa.yaml`
  - `nodejs-hpa.yaml`
  - `alert-watcher.yaml`

## Backend concept (simple)

This repository uses minimal stub services so the focus stays on DevOps deployment rather than full backend engineering.

- `fastapi/main.py`: simple API service that connects to PostgreSQL and stores/retrieves user data.
- `nodejs/app.js`: lightweight web service that calls the API service over HTTP and exposes its own health endpoint.
- `worker/worker.py`: continuous worker process that keeps running and exposes `/health`.
- `alert-watcher/watcher.py`: cluster-side watcher that monitors deployment health and sends email alerts when all replicas fail.

Each backend file is intentionally small and focused on one job for deployment testing.

## How this satisfies the requirement

1. Service → connects to RDS
   - Implemented in `fastapi/main.py`
   - Uses `psycopg2` and DB credentials from `k8s/secret-db.yaml`

2. Service → calls another service (HTTP)
   - Web service calls the API service in `nodejs/app.js` via `/fetch-users` and `/ping-fastapi`
   - API service calls the web service in `fastapi/main.py` via `/node-health`

3. Kubernetes → runs 2 replicas
   - `k8s/fastapi-deployment.yaml`
   - `k8s/nodejs-deployment.yaml`
   - `k8s/worker-deployment.yaml`

4. HPA → scales based on load
   - `k8s/fastapi-hpa.yaml`
   - `k8s/nodejs-hpa.yaml`
   - Requires Metrics Server installed in the cluster

5. Worker → runs continuously
   - `worker/worker.py` runs an infinite loop and exposes `/health` on port `8080`
   - `k8s/worker-deployment.yaml` and `k8s/worker-service.yaml`

6. Email → sent on failure
   - Implemented in `alert-watcher/watcher.py`
   - Deployed with `k8s/alert-watcher.yaml`
   - Monitors `fastapi` and `nodejs` deployments and sends email if all replicas fail

7. Secrets
   - `k8s/secret-db.yaml` stores DB credentials in a Kubernetes Secret
   - Used by `fastapi` Deployment environment variables

8. Health check scheduler
   - `fastapi/main.py` starts a 5-minute self-health scheduler
   - `nodejs/app.js` starts a 5-minute self-health scheduler
   - Both expose `/health`

## Terraform infrastructure creation

Terraform creates the AWS infrastructure for the project:
- Amazon RDS PostgreSQL instance
- Amazon EKS cluster with managed node group

Files:
- `terraform/main.tf`
- `terraform/variables.tf`
- `terraform/outputs.tf`
- `terraform/terraform.tfvars.example`

Deploy infrastructure with Terraform:

```bash
cd c:\Users\sudi.venkatesh\Documents\Deployement\terraform
terraform init
terraform apply
```

After creation, copy the output values into `k8s/secret-db.yaml`:
- `db_endpoint` → `DB_HOST`
- `db_port` → `DB_PORT`
- `db_name` → `DB_NAME`

Also configure your local `kubectl` to use the new EKS cluster before applying Kubernetes manifests.

## Deployment steps

1. Build container images:

```bash
cd c:\Users\sudi.venkatesh\Documents\Deployement
docker build -t fastapi-service:latest ./fastapi
docker build -t nodejs-service:latest ./nodejs
docker build -t worker-service:latest ./worker
docker build -t alert-watcher-service:latest ./alert-watcher
```

2. Replace `YOUR_RDS_ENDPOINT` in `k8s/secret-db.yaml` with the actual RDS host.

3. Apply the Kubernetes manifests:

```bash
kubectl apply -f k8s/secret-db.yaml
kubectl apply -f k8s/fastapi-deployment.yaml
kubectl apply -f k8s/fastapi-service.yaml
kubectl apply -f k8s/nodejs-deployment.yaml
kubectl apply -f k8s/nodejs-service.yaml
kubectl apply -f k8s/worker-deployment.yaml
kubectl apply -f k8s/worker-service.yaml
kubectl apply -f k8s/fastapi-hpa.yaml
kubectl apply -f k8s/nodejs-hpa.yaml
kubectl apply -f k8s/alert-watcher.yaml
```

4. Ensure Metrics Server is installed for HPA to work.

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

5. Verify the services:

```bash
kubectl get pods
kubectl get deployments
kubectl get hpa
```

## Example API calls

- API service health: `GET /health`
- Web service health: `GET /health`
- Create a user:

```bash
curl -X POST http://<fastapi-host>:8000/users -H 'Content-Type: application/json' -d '{"name":"Alice","email":"alice@example.com"}'
```

- Fetch users:

```bash
curl http://<fastapi-host>:8000/users
```

- Web service fetching users from the API service:

```bash
curl http://<nodejs-host>:3000/fetch-users
```

## Notes

- `fastapi/main.py` uses PostgreSQL and must receive valid RDS credentials.
- `nodejs/app.js` communicates with the API service using the internal cluster service `fastapi-service`.
- `alert-watcher` requires SMTP configuration and RBAC privileges.
- Replace placeholder values in `k8s/secret-db.yaml` and `k8s/alert-watcher.yaml` before production use.
