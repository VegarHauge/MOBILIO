#!/bin/bash
# Complete GKE Deployment Script
# This script builds Docker images, pushes to GCR, and deploys all services to GKE

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-dat515-478210}"
REGION="${GCP_REGION:-europe-north1}"
CLUSTER_NAME="shop-app-cluster"
NAMESPACE="shop-app"

# Image versions
BACKEND_VERSION="${BACKEND_VERSION:-v1}"
FRONTEND_VERSION="${FRONTEND_VERSION:-v3}"
RECOMMENDATION_VERSION="${RECOMMENDATION_VERSION:-v1}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# Error handler
error_exit() {
    log_error "$1"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log_step "Checking prerequisites..."
    
    command -v gcloud >/dev/null 2>&1 || error_exit "gcloud CLI not installed. Install from: https://cloud.google.com/sdk/docs/install"
    command -v kubectl >/dev/null 2>&1 || error_exit "kubectl not installed. Install from: https://kubernetes.io/docs/tasks/tools/"
    command -v docker >/dev/null 2>&1 || error_exit "Docker not installed. Install from: https://docs.docker.com/get-docker/"
    
    # Check if logged in to gcloud
    gcloud auth list --filter=status:ACTIVE --format="value(account)" >/dev/null 2>&1 || \
        error_exit "Not logged in to gcloud. Run: gcloud auth login"
    
    # Verify project
    CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
    if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
        log_warn "Current project is $CURRENT_PROJECT, setting to $PROJECT_ID"
        gcloud config set project $PROJECT_ID
    fi
    
    log_info "All prerequisites met ✓"
}

# Get cluster credentials
get_cluster_credentials() {
    log_step "Getting cluster credentials..."
    
    if ! gcloud container clusters describe $CLUSTER_NAME --region=$REGION >/dev/null 2>&1; then
        error_exit "Cluster $CLUSTER_NAME not found in region $REGION. Create it first or update CLUSTER_NAME/REGION variables."
    fi
    
    gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION
    log_info "Connected to cluster $CLUSTER_NAME ✓"
}

# Build Docker images
build_images() {
    log_step "Building Docker images..."
    
    cd "$(dirname "$0")/.." || error_exit "Failed to change directory"
    
    log_info "Building backend image..."
    docker build --platform linux/amd64 \
        -t gcr.io/$PROJECT_ID/backend:$BACKEND_VERSION \
        -t gcr.io/$PROJECT_ID/backend:latest \
        ./backend || error_exit "Failed to build backend image"
    
    log_info "Building frontend image..."
    docker build --platform linux/amd64 \
        -t gcr.io/$PROJECT_ID/frontend:$FRONTEND_VERSION \
        -t gcr.io/$PROJECT_ID/frontend:latest \
        ./frontend || error_exit "Failed to build frontend image"
    
    log_info "Building recommendation image..."
    docker build --platform linux/amd64 \
        -t gcr.io/$PROJECT_ID/recommendation:$RECOMMENDATION_VERSION \
        -t gcr.io/$PROJECT_ID/recommendation:latest \
        ./recomendation || error_exit "Failed to build recommendation image"
    
    log_info "All images built successfully ✓"
}

# Push images to GCR
push_images() {
    log_step "Pushing images to Google Container Registry..."
    
    # Configure Docker for GCR
    gcloud auth configure-docker --quiet
    
    log_info "Pushing backend:$BACKEND_VERSION..."
    docker push gcr.io/$PROJECT_ID/backend:$BACKEND_VERSION
    docker push gcr.io/$PROJECT_ID/backend:latest
    
    log_info "Pushing frontend:$FRONTEND_VERSION..."
    docker push gcr.io/$PROJECT_ID/frontend:$FRONTEND_VERSION
    docker push gcr.io/$PROJECT_ID/frontend:latest
    
    log_info "Pushing recommendation:$RECOMMENDATION_VERSION..."
    docker push gcr.io/$PROJECT_ID/recommendation:$RECOMMENDATION_VERSION
    docker push gcr.io/$PROJECT_ID/recommendation:latest
    
    log_info "All images pushed successfully ✓"
}

# Deploy Kubernetes resources
deploy_kubernetes() {
    log_step "Deploying to Kubernetes..."
    
    # Create namespace if not exists
    log_info "Creating namespace: $NAMESPACE"
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
    
    # Deploy persistent volumes first
    log_info "Deploying persistent volumes..."
    kubectl apply -f k8s/mysql/pvc.yaml
    kubectl apply -f k8s/analyticsdb/pvc.yaml
    
    # Deploy databases
    log_info "Deploying databases..."
    kubectl apply -f k8s/mysql/deployment.yaml
    kubectl apply -f k8s/mysql/service.yaml
    kubectl apply -f k8s/analyticsdb/deployment.yaml
    kubectl apply -f k8s/analyticsdb/service.yaml
    
    log_info "Waiting for databases to be ready..."
    kubectl wait --for=condition=ready pod -l app=mysql -n $NAMESPACE --timeout=180s
    kubectl wait --for=condition=ready pod -l app=analyticsdb -n $NAMESPACE --timeout=180s
    
    # Deploy Redis
    log_info "Deploying Redis..."
    kubectl apply -f k8s/redis/deployment.yaml
    kubectl apply -f k8s/redis/service.yaml
    kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=120s
    
    # Deploy backend services
    log_info "Deploying backend..."
    kubectl apply -f k8s/backend/secret.yaml
    kubectl apply -f k8s/backend/deployment.yaml
    kubectl apply -f k8s/backend/service.yaml
    kubectl wait --for=condition=available deployment/backend -n $NAMESPACE --timeout=180s
    
    # Deploy recommendation service
    log_info "Deploying recommendation service..."
    kubectl apply -f k8s/recommendation/deployment.yaml
    kubectl apply -f k8s/recommendation/service.yaml
    kubectl wait --for=condition=available deployment/recommendation -n $NAMESPACE --timeout=180s
    
    # Deploy frontend
    log_info "Deploying frontend..."
    kubectl apply -f k8s/frontend/deployment.yaml
    kubectl apply -f k8s/frontend/service.yaml
    kubectl wait --for=condition=available deployment/frontend -n $NAMESPACE --timeout=180s
    
    # Deploy nginx reverse proxy
    log_info "Deploying nginx reverse proxy..."
    kubectl apply -f k8s/nginx/configmap.yaml
    kubectl apply -f k8s/nginx/deployment.yaml
    kubectl apply -f k8s/nginx/service.yaml
    kubectl wait --for=condition=available deployment/nginx -n $NAMESPACE --timeout=180s
    
    # Deploy monitoring stack
    log_info "Deploying Prometheus..."
    kubectl apply -f k8s/prometheus/configmap.yaml
    kubectl apply -f k8s/prometheus/deployment.yaml
    kubectl apply -f k8s/prometheus/service.yaml
    
    log_info "Deploying Grafana..."
    kubectl apply -f k8s/grafana/deployment.yaml
    kubectl apply -f k8s/grafana/service.yaml
    
    kubectl wait --for=condition=available deployment/prometheus -n $NAMESPACE --timeout=120s
    kubectl wait --for=condition=available deployment/grafana -n $NAMESPACE --timeout=120s
    
    log_info "All services deployed successfully ✓"
}

# Wait for external IP
wait_for_external_ip() {
    log_step "Waiting for LoadBalancer external IP..."
    
    for i in {1..30}; do
        EXTERNAL_IP=$(kubectl get svc nginx -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
        if [ -n "$EXTERNAL_IP" ]; then
            log_info "External IP assigned: $EXTERNAL_IP ✓"
            echo "$EXTERNAL_IP" > .external-ip
            return 0
        fi
        echo -n "."
        sleep 10
    done
    
    log_warn "Timeout waiting for external IP. Check manually with: kubectl get svc nginx -n $NAMESPACE"
    return 1
}

# Initialize database
initialize_database() {
    log_step "Initializing database..."
    
    log_info "Running schema creation..."
    kubectl exec -i -n $NAMESPACE deployment/mysql -- \
        mysql -udat515user -padmin123 DAT515 < db/main/init.sql || \
        error_exit "Failed to initialize database schema"
    
    log_info "Database initialized successfully ✓"
    log_warn "Run './scripts/seed-db.sh' to populate with test data"
}

# Setup monitoring
setup_monitoring() {
    log_step "Setting up monitoring..."
    
    if [ -f .external-ip ]; then
        EXTERNAL_IP=$(cat .external-ip)
    else
        EXTERNAL_IP=$(kubectl get svc nginx -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
    fi
    
    if [ -z "$EXTERNAL_IP" ]; then
        log_warn "No external IP found. Skipping Grafana setup."
        return 0
    fi
    
    log_info "Waiting for Grafana to be fully ready..."
    sleep 15
    
    log_info "Adding Prometheus data source to Grafana..."
    curl -X POST "http://$EXTERNAL_IP/grafana/api/datasources" \
        -H "Content-Type: application/json" \
        -u "admin:admin" \
        -d '{
            "name": "Prometheus",
            "type": "prometheus",
            "url": "http://prometheus:9090",
            "access": "proxy",
            "isDefault": true,
            "jsonData": {
                "httpMethod": "POST"
            }
        }' >/dev/null 2>&1 || log_warn "Failed to add Prometheus datasource (may already exist)"
    
    log_info "Importing Grafana dashboard..."
    if [ -f monitoring/grafana/dashboards/fastapi_metrics.json ]; then
        DASHBOARD_JSON=$(cat monitoring/grafana/dashboards/fastapi_metrics.json | jq 'del(.id)')
        curl -X POST "http://$EXTERNAL_IP/grafana/api/dashboards/db" \
            -H "Content-Type: application/json" \
            -u "admin:admin" \
            -d "{\"dashboard\": $DASHBOARD_JSON, \"overwrite\": true}" \
            >/dev/null 2>&1 || log_warn "Failed to import dashboard (may already exist)"
    fi
    
    log_info "Monitoring setup complete ✓"
}

# Print deployment summary
print_summary() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                   DEPLOYMENT SUCCESSFUL! 🎉                    ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    
    if [ -f .external-ip ]; then
        EXTERNAL_IP=$(cat .external-ip)
    else
        EXTERNAL_IP=$(kubectl get svc nginx -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
    fi
    
    if [ -n "$EXTERNAL_IP" ]; then
        echo "Application URL:       http://$EXTERNAL_IP"
        echo "API Documentation:     http://$EXTERNAL_IP/api/docs"
        echo "Grafana Monitoring:    http://$EXTERNAL_IP/grafana/"
        echo "   └─ Credentials:        admin / admin"
        echo ""
    else
        echo "Waiting for external IP assignment..."
        echo "Check with: kubectl get svc nginx -n $NAMESPACE"
        echo ""
    fi
    
    echo "Useful Commands:"
    echo "View all pods:         kubectl get pods -n $NAMESPACE"
    echo "View services:         kubectl get svc -n $NAMESPACE"
    echo "View logs:             kubectl logs -f deployment/<name> -n $NAMESPACE"
    echo "Seed database:         ./scripts/seed-db.sh"
    echo ""
    echo "Cost Management:"
    echo "View costs:            https://console.cloud.google.com/billing?project=$PROJECT_ID"
    echo "Estimated cost:        ~\$116/month (~\$3.80/day)"
    echo ""
    echo "Cleanup (DELETE CLUSTER):"
    echo "gcloud container clusters delete $CLUSTER_NAME --region=$REGION"
    echo ""
}

# Main execution
main() {
    echo ""
    log_step "Starting GKE Deployment Process..."
    echo ""
    
    check_prerequisites
    get_cluster_credentials
    build_images
    push_images
    deploy_kubernetes
    wait_for_external_ip
    initialize_database
    setup_monitoring
    print_summary
    
    log_info "Deployment complete! ✓"
}

# Run main function
main "$@"
