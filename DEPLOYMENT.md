# ALIE Platform - Deployment Guide

## 🚀 Overview

This guide covers deploying ALIE (AI Lead Intelligence Engine) to production using Docker, Kubernetes, and CI/CD automation.

## 📋 Prerequisites

### Required Tools
- Docker 24.0+
- Docker Compose 2.20+
- kubectl 1.28+
- Kubernetes cluster (GKE, EKS, AKS, or self-hosted)
- Helm 3.12+ (optional, for package management)

### Required Accounts
- GitHub account (for CI/CD)
- Container registry (GitHub Container Registry, Docker Hub, or private registry)
- Kubernetes cluster access
- SSL certificate (Let's Encrypt via cert-manager)

### Required Secrets
```bash
# API Keys
OPENAI_API_KEY=sk-xxx
OPENAI_ASSISTANT_ID=asst_xxx
TWOGIS_API_KEY=xxx
GOOGLE_PLACES_KEY=xxx
APIFY_TOKEN=xxx

# Database credentials
POSTGRES_USER=alie_user
POSTGRES_PASSWORD=secure_password_here
REDIS_PASSWORD=secure_redis_password

# Application secrets
SECRET_KEY=generate_with_openssl_rand_hex_32
```

---

## 🐳 Local Development with Docker

### Step 1: Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and fill in your values
nano .env
```

### Step 2: Build Images

```bash
# Build all images
docker-compose build

# Or build individually
docker build -t alie-api:latest -f Dockerfile .
docker build -t alie-worker:latest -f Dockerfile.worker .
docker build -t alie-beat:latest -f Dockerfile.beat .
```

### Step 3: Start Services

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
docker-compose logs -f worker
```

### Step 4: Initialize Database

```bash
# Run migrations
docker-compose exec api alembic upgrade head

# (Optional) Load sample data
docker-compose exec api python -m backend.scripts.seed_data
```

### Step 5: Verify

```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs

# Test recommendation
curl -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_query": "Найти строителя в Алматы", "location": "Almaty"}'
```

---

## ☸️ Kubernetes Deployment

### Step 1: Prepare Cluster

```bash
# Verify cluster access
kubectl cluster-info
kubectl get nodes

# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Install cert-manager (for SSL certificates)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

### Step 2: Create Namespace

```bash
kubectl apply -f k8s/namespace.yaml
```

### Step 3: Configure Secrets

**Option 1: From command line**

```bash
kubectl create secret generic alie-secrets \
  --namespace=alie-prod \
  --from-literal=POSTGRES_USER='alie_user' \
  --from-literal=POSTGRES_PASSWORD='your_secure_password' \
  --from-literal=REDIS_PASSWORD='your_redis_password' \
  --from-literal=OPENAI_API_KEY='sk-xxx' \
  --from-literal=OPENAI_ASSISTANT_ID='asst_xxx' \
  --from-literal=TWOGIS_API_KEY='xxx' \
  --from-literal=GOOGLE_PLACES_KEY='xxx' \
  --from-literal=APIFY_TOKEN='xxx' \
  --from-literal=SECRET_KEY='xxx' \
  --from-literal=CELERY_BROKER_URL='redis://:your_redis_password@redis-service:6379/1' \
  --from-literal=CELERY_RESULT_BACKEND='redis://:your_redis_password@redis-service:6379/2'
```

**Option 2: From file**

```bash
# Edit k8s/secrets.yaml with your values
kubectl apply -f k8s/secrets.yaml
```

### Step 4: Apply ConfigMap

```bash
kubectl apply -f k8s/configmap.yaml
```

### Step 5: Deploy Database Layer

```bash
# Deploy PostgreSQL
kubectl apply -f k8s/postgres-deployment.yaml

# Wait for readiness
kubectl wait --for=condition=ready pod -l app=postgres -n alie-prod --timeout=300s

# Deploy Redis
kubectl apply -f k8s/redis-deployment.yaml

# Wait for readiness
kubectl wait --for=condition=ready pod -l app=redis -n alie-prod --timeout=300s
```

### Step 6: Deploy Application Layer

```bash
# Deploy API
kubectl apply -f k8s/api-deployment.yaml

# Deploy Celery Worker
kubectl apply -f k8s/worker-deployment.yaml

# Deploy Celery Beat
kubectl apply -f k8s/beat-deployment.yaml

# Wait for all deployments
kubectl rollout status deployment/alie-api -n alie-prod
kubectl rollout status deployment/alie-worker -n alie-prod
kubectl rollout status deployment/alie-beat -n alie-prod
```

### Step 7: Configure Ingress

```bash
# Update k8s/ingress.yaml with your domain
# Change api.alie.kz to your domain
# Change admin@alie.kz to your email

kubectl apply -f k8s/ingress.yaml

# Get external IP
kubectl get ingress -n alie-prod
```

### Step 8: Run Migrations

```bash
kubectl exec -n alie-prod deployment/alie-api -- alembic upgrade head
```

### Step 9: Verify Deployment

```bash
# Check all resources
kubectl get all -n alie-prod

# Check pod logs
kubectl logs -n alie-prod -l app=alie-api --tail=100
kubectl logs -n alie-prod -l app=alie-worker --tail=100

# Check pod health
kubectl describe pod -n alie-prod -l app=alie-api

# Test endpoint
curl https://api.alie.kz/health
```

---

## 🔄 CI/CD with GitHub Actions

### Step 1: Configure Repository Secrets

Go to **Settings → Secrets and variables → Actions** and add:

```
KUBE_CONFIG          # Base64-encoded kubeconfig file
POSTGRES_USER        # Database username
POSTGRES_PASSWORD    # Database password
REDIS_PASSWORD       # Redis password
OPENAI_API_KEY       # OpenAI API key
OPENAI_ASSISTANT_ID  # OpenAI Assistant ID
TWOGIS_API_KEY       # 2GIS API key
GOOGLE_PLACES_KEY    # Google Places API key
APIFY_TOKEN          # Apify token
SECRET_KEY           # Application secret key
CELERY_BROKER_URL    # Full Celery broker URL
CELERY_RESULT_BACKEND # Full Celery result backend URL
```

**Generate KUBE_CONFIG:**

```bash
# Encode your kubeconfig
cat ~/.kube/config | base64 -w 0
```

### Step 2: Enable GitHub Container Registry

```bash
# Create personal access token with packages:write scope
# https://github.com/settings/tokens

# Login to GHCR locally
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Tag and push images
docker tag alie-api:latest ghcr.io/YOUR_USERNAME/alie-api:latest
docker tag alie-worker:latest ghcr.io/YOUR_USERNAME/alie-worker:latest
docker tag alie-beat:latest ghcr.io/YOUR_USERNAME/alie-beat:latest

docker push ghcr.io/YOUR_USERNAME/alie-api:latest
docker push ghcr.io/YOUR_USERNAME/alie-worker:latest
docker push ghcr.io/YOUR_USERNAME/alie-beat:latest
```

### Step 3: Update Kubernetes Manifests

Edit `k8s/api-deployment.yaml`, `k8s/worker-deployment.yaml`, `k8s/beat-deployment.yaml`:

```yaml
# Change:
image: ghcr.io/your-username/alie-api:latest

# To:
image: ghcr.io/YOUR_ACTUAL_USERNAME/alie-api:latest
```

### Step 4: Trigger Deployment

**Automatic deployment on push:**

```bash
git add .
git commit -m "feat: add deployment configuration"
git push origin main
```

The CI/CD pipeline will:
1. Lint code
2. Run tests
3. Build Docker images
4. Push to GitHub Container Registry
5. Deploy to Kubernetes
6. Run smoke tests

**Manual deployment:**

Go to **Actions → Deploy to Production → Run workflow**

---

## 📊 Monitoring & Observability

### Health Checks

```bash
# API health
curl https://api.alie.kz/health

# Kubernetes pod health
kubectl get pods -n alie-prod

# Application metrics
curl https://api.alie.kz/metrics
```

### Logs

```bash
# Recent logs (last 100 lines)
kubectl logs -n alie-prod -l app=alie-api --tail=100

# Stream logs in real-time
kubectl logs -n alie-prod -l app=alie-api -f

# Logs from specific pod
kubectl logs -n alie-prod <pod-name>

# Celery worker logs
kubectl logs -n alie-prod -l app=alie-worker --tail=100
```

### Resource Usage

```bash
# CPU and memory usage
kubectl top pods -n alie-prod
kubectl top nodes

# Horizontal Pod Autoscaler status
kubectl get hpa -n alie-prod

# Describe HPA
kubectl describe hpa alie-api-hpa -n alie-prod
```

---

## 🛠 Maintenance

### Scaling

```bash
# Manual scaling
kubectl scale deployment alie-api --replicas=5 -n alie-prod
kubectl scale deployment alie-worker --replicas=10 -n alie-prod

# Autoscaling is already configured via HPA
# API: 3-10 replicas (based on CPU/memory)
# Worker: 2-8 replicas (based on CPU/memory)
```

### Updates

```bash
# Update image
kubectl set image deployment/alie-api \
  api=ghcr.io/YOUR_USERNAME/alie-api:v1.1.0 \
  -n alie-prod

# Rollout status
kubectl rollout status deployment/alie-api -n alie-prod

# Rollout history
kubectl rollout history deployment/alie-api -n alie-prod
```

### Rollback

```bash
# Rollback to previous version
kubectl rollout undo deployment/alie-api -n alie-prod

# Rollback to specific revision
kubectl rollout undo deployment/alie-api --to-revision=2 -n alie-prod
```

### Database Migrations

```bash
# Run migrations
kubectl exec -n alie-prod deployment/alie-api -- alembic upgrade head

# Rollback migration
kubectl exec -n alie-prod deployment/alie-api -- alembic downgrade -1

# Check migration status
kubectl exec -n alie-prod deployment/alie-api -- alembic current
```

### Backup

```bash
# Backup PostgreSQL
kubectl exec -n alie-prod deployment/postgres -- \
  pg_dump -U alie_user alie > backup_$(date +%Y%m%d).sql

# Restore PostgreSQL
kubectl exec -i -n alie-prod deployment/postgres -- \
  psql -U alie_user alie < backup_20240305.sql
```

---

## 🔒 Security Best Practices

### 1. Secrets Management

- ✅ Never commit secrets to version control
- ✅ Use Kubernetes Secrets or external secret managers (Vault, AWS Secrets Manager)
- ✅ Rotate secrets regularly
- ✅ Use RBAC to restrict secret access

### 2. Network Security

- ✅ Enable Network Policies
- ✅ Use TLS for all external traffic (enforced via Ingress)
- ✅ Restrict egress traffic

### 3. Container Security

- ✅ Run containers as non-root user (already configured)
- ✅ Scan images for vulnerabilities (Trivy in CI)
- ✅ Use minimal base images (alpine)
- ✅ Keep dependencies updated

### 4. Access Control

- ✅ Use RBAC for kubectl access
- ✅ Enable Pod Security Standards
- ✅ Audit logs enabled

---

## 🐛 Troubleshooting

### Pods not starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n alie-prod

# Check events
kubectl get events -n alie-prod --sort-by='.lastTimestamp'

# Check logs
kubectl logs <pod-name> -n alie-prod --previous
```

### Database connection issues

```bash
# Test connection from API pod
kubectl exec -n alie-prod deployment/alie-api -- \
  psql -h postgres-service -U alie_user -d alie -c "SELECT 1"

# Check if PostgreSQL is running
kubectl get pods -n alie-prod -l app=postgres
```

### Redis connection issues

```bash
# Test connection
kubectl exec -n alie-prod deployment/alie-api -- \
  redis-cli -h redis-service -a $REDIS_PASSWORD ping

# Check if Redis is running
kubectl get pods -n alie-prod -l app=redis
```

### SSL certificate issues

```bash
# Check certificate status
kubectl get certificate -n alie-prod

# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager

# Manually trigger certificate issuance
kubectl delete certificate alie-api-cert -n alie-prod
kubectl apply -f k8s/ingress.yaml
```

### Performance issues

```bash
# Check resource usage
kubectl top pods -n alie-prod

# Check HPA status
kubectl get hpa -n alie-prod

# Scale manually if needed
kubectl scale deployment alie-api --replicas=10 -n alie-prod
```

---

## 📞 Support

For issues and questions:
- GitHub Issues: https://github.com/YOUR_USERNAME/alie/issues
- Documentation: https://docs.alie.kz
- Email: support@alie.kz

---

## 📝 Checklist

### Pre-Deployment
- [ ] Docker installed and configured
- [ ] Kubernetes cluster provisioned
- [ ] kubectl configured
- [ ] Domain name configured
- [ ] SSL certificate ready (or cert-manager installed)
- [ ] All secrets prepared
- [ ] GitHub Container Registry configured

### Deployment
- [ ] Namespace created
- [ ] ConfigMap applied
- [ ] Secrets created
- [ ] PostgreSQL deployed and healthy
- [ ] Redis deployed and healthy
- [ ] API deployed and healthy
- [ ] Worker deployed and healthy
- [ ] Beat deployed and healthy
- [ ] Ingress configured
- [ ] SSL certificate issued
- [ ] Database migrations run

### Post-Deployment
- [ ] Health checks passing
- [ ] API accessible via HTTPS
- [ ] Logs configured
- [ ] Monitoring set up
- [ ] Backups scheduled
- [ ] Documentation updated
- [ ] Team notified

---

**Last Updated:** March 2026  
**Version:** 1.0.0
