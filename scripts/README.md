# Deployment Scripts

This directory contains automation scripts for deploying the shop application to Google Kubernetes Engine (GKE).

## Scripts Overview

When to use which:

Use update.sh when:
✅ You changed backend Python code
✅ You changed frontend React code
✅ You modified Dockerfile
✅ You added new dependencies

Use restart.sh when:
✅ You updated nginx configmap
✅ You updated Kubernetes secrets
✅ Pod is stuck/crashed
✅ You want to clear pod state

Use deploy.sh when:
✅ First-time deployment
✅ Major infrastructure changes
✅ Adding new services

### 1. `deploy.sh` - Complete Deployment

Main deployment script that handles the entire deployment process.

**What it does:**

- Checks prerequisites (gcloud, kubectl, docker)
- Builds Docker images for all services
- Pushes images to Google Container Registry
- Deploys all Kubernetes resources
- Initializes database schema
- Sets up monitoring (Prometheus + Grafana)

**Usage:**

```bash
# Basic deployment
./scripts/deploy.sh

# With custom configuration
export BACKEND_VERSION=v2
export FRONTEND_VERSION=v4
./scripts/deploy.sh
```

**Prerequisites:**

- Google Cloud SDK installed
- kubectl installed
- Docker Desktop running
- GKE cluster already created
- Authenticated with `gcloud auth login`

**Duration:** ~10-15 minutes (first time), ~5-8 minutes (subsequent)

---

### 2. `seed-db.sh` - Database Seeding

Populates the database with realistic test data.

**What it does:**

- Creates admin and customer user accounts
- Adds 180+ products across 6 categories
- Generates realistic order history
- Creates cart items for active users

**Usage:**

```bash
# Seed with 100 users (default)
./scripts/seed-db.sh

# Seed with custom number of users
./scripts/seed-db.sh --users 50

# Custom namespace
./scripts/seed-db.sh --namespace my-namespace
```

**Creates:**

- 1 admin user (admin@shop.com / admin123)
- N customer users (customer_1@example.com ... customer_N@example.com / password123)
- ~180 products
- ~157 orders with realistic behavior

**Duration:** ~30-60 seconds

---

### 3. `cleanup.sh` - Resource Cleanup

Removes all deployed resources from Kubernetes.

**What it does:**

- Deletes all resources in the shop-app namespace
- Removes LoadBalancer (stops external IP charges)
- Deletes persistent volumes (⚠️ DATA LOSS)
- Optionally deletes the entire GKE cluster

**Usage:**

```bash
# Delete all resources but keep cluster
./scripts/cleanup.sh

# Delete everything including cluster
./scripts/cleanup.sh --delete-cluster
```

**⚠️ WARNING:** This is destructive! All data will be lost.

---

## Typical Workflow

### First-Time Deployment

```bash
# 1. Create GKE cluster (if not already created)
gcloud container clusters create shop-app-cluster \
  --region europe-north1 \
  --num-nodes 3 \
  --machine-type e2-small

# 2. Deploy application
cd /path/to/7project
./scripts/deploy.sh

# 3. Seed database with test data
./scripts/seed-db.sh --users 100

# 4. Access application
# URL will be shown at end of deploy.sh
```

### Making Changes & Redeploying

```bash
# 1. Make code changes to backend/frontend

# 2. Rebuild and redeploy
export BACKEND_VERSION=v2
./scripts/deploy.sh

# 3. Verify changes
kubectl get pods -n shop-app
```

### Cleanup After Testing

```bash
# Keep cluster, delete app resources
./scripts/cleanup.sh

# Delete everything (stops all charges)
./scripts/cleanup.sh --delete-cluster
```

---

## Environment Variables

### `deploy.sh` Configuration

```bash
GCP_PROJECT_ID       # Google Cloud project ID (default: dat515-478210)
GCP_REGION           # GKE region (default: europe-north1)
BACKEND_VERSION      # Backend image version (default: v1)
FRONTEND_VERSION     # Frontend image version (default: v3)
RECOMMENDATION_VERSION # Recommendation image version (default: v1)
```

### `seed-db.sh` Configuration

```bash
NAMESPACE            # Kubernetes namespace (default: shop-app)
NUM_USERS            # Number of customer users (default: 100)
```

---

## Troubleshooting

### "Cluster not found"

```bash
# Verify cluster exists
gcloud container clusters list --region=europe-north1

# Get credentials
gcloud container clusters get-credentials shop-app-cluster --region=europe-north1
```

### "Image pull error"

```bash
# Ensure Docker is configured for GCR
gcloud auth configure-docker

# Verify images exist
gcloud container images list --repository=gcr.io/dat515-478210
```

### "Pod not ready"

```bash
# Check pod status
kubectl get pods -n shop-app

# View logs
kubectl logs -f deployment/backend -n shop-app

# Describe pod for events
kubectl describe pod <pod-name> -n shop-app
```

### "Database connection failed"

```bash
# Verify MySQL is running
kubectl get pods -n shop-app -l app=mysql

# Check MySQL logs
kubectl logs deployment/mysql -n shop-app

# Test connection
kubectl exec -it deployment/mysql -n shop-app -- \
  mysql -udat515user -padmin123 -e "SELECT 1"
```

---

## Cost Optimization

### Daily Development Pattern

```bash
# Morning: Start cluster
gcloud container clusters resize shop-app-cluster \
  --region=europe-north1 \
  --num-nodes=3

# Evening: Stop cluster (scale to 0)
gcloud container clusters resize shop-app-cluster \
  --region=europe-north1 \
  --num-nodes=0
```

### Complete Shutdown

```bash
# Delete cluster (no charges except storage)
./scripts/cleanup.sh --delete-cluster

# To redeploy later, recreate cluster and run deploy.sh
```

---

## Script Architecture

```
scripts/
├── deploy.sh           # Main orchestration script
│   ├── check_prerequisites()
│   ├── build_images()
│   ├── push_images()
│   ├── deploy_kubernetes()
│   ├── initialize_database()
│   └── setup_monitoring()
│
├── seed-db.sh          # Data population
│   ├── check_backend()
│   ├── check_mysql()
│   ├── seed_database()
│   └── verify_data()
│
└── cleanup.sh          # Resource removal
    ├── delete_namespace()
    └── delete_cluster() [optional]
```

---

## Best Practices

1. **Always check costs** after deployment:

   ```bash
   gcloud billing projects describe dat515-478210
   ```

2. **Monitor your credits**:

   ```bash
   # View in console
   https://console.cloud.google.com/billing
   ```

3. **Use version tags** for images:

   ```bash
   export BACKEND_VERSION=v2.1-stable
   ./scripts/deploy.sh
   ```

4. **Test locally first** before deploying:

   ```bash
   docker-compose up
   ```

5. **Always cleanup** when done testing:
   ```bash
   ./scripts/cleanup.sh --delete-cluster
   ```

---

## CI/CD Integration (Future Enhancement)

These scripts can be integrated into GitHub Actions:

```yaml
# .github/workflows/deploy.yml
name: Deploy to GKE
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy
        run: ./scripts/deploy.sh
        env:
          GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
```

---

## Support

For issues or questions:

1. Check logs: `kubectl logs -f deployment/<name> -n shop-app`
2. View pod status: `kubectl describe pod <name> -n shop-app`
3. Check GCP Console: https://console.cloud.google.com/kubernetes
