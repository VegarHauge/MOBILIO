#!/bin/bash
# Update Individual Services Script
# Rebuilds and redeploys specific services without full redeployment

set -euo pipefail

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-dat515-478210}"
NAMESPACE="shop-app"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

error_exit() {
    log_error "$1"
    exit 1
}

# Show usage
show_usage() {
    echo "Usage: $0 <service> [version]"
    echo ""
    echo "Services:"
    echo "  backend              Update backend service"
    echo "  frontend             Update frontend service"
    echo "  recommendation       Update recommendation service"
    echo "  nginx                Update nginx configuration"
    echo "  grafana              Restart Grafana"
    echo "  prometheus           Restart Prometheus"
    echo "  all                  Update all application services (backend, frontend, recommendation)"
    echo ""
    echo "Examples:"
    echo "  $0 backend           # Rebuild and update backend with auto-incremented version"
    echo "  $0 backend v2        # Rebuild and update backend with specific version"
    echo "  $0 frontend          # Rebuild and update frontend"
    echo "  $0 nginx             # Restart nginx (after config changes)"
    echo "  $0 all               # Update all services"
    echo ""
}

# Get next version number
get_next_version() {
    local service=$1
    local current_image=$(kubectl get deployment/$service -n $NAMESPACE -o jsonpath='{.spec.template.spec.containers[0].image}' 2>/dev/null)
    
    if [[ $current_image =~ :v([0-9]+)$ ]]; then
        local current_version="${BASH_REMATCH[1]}"
        local next_version=$((current_version + 1))
        echo "v$next_version"
    else
        echo "v1"
    fi
}

# Build and push image
build_and_push() {
    local service=$1
    local version=$2
    local service_dir=$3
    
    log_step "Building $service:$version..."
    
    cd "$(dirname "$0")/.." || error_exit "Failed to change directory"
    
    docker build --platform linux/amd64 \
        -t gcr.io/$PROJECT_ID/$service:$version \
        -t gcr.io/$PROJECT_ID/$service:latest \
        ./$service_dir || error_exit "Failed to build $service"
    
    log_step "Pushing $service:$version to GCR..."
    docker push gcr.io/$PROJECT_ID/$service:$version
    docker push gcr.io/$PROJECT_ID/$service:latest
    
    log_info "$service:$version built and pushed ✓"
}

# Update deployment
update_deployment() {
    local service=$1
    local version=$2
    
    log_step "Updating $service deployment..."
    
    kubectl set image deployment/$service \
        $service=gcr.io/$PROJECT_ID/$service:$version \
        -n $NAMESPACE || error_exit "Failed to update deployment"
    
    log_info "Waiting for rollout to complete..."
    kubectl rollout status deployment/$service -n $NAMESPACE --timeout=300s || \
        error_exit "Rollout failed"
    
    log_info "$service updated successfully ✓"
}

# Restart deployment (without rebuild)
restart_deployment() {
    local service=$1
    
    log_step "Restarting $service..."
    kubectl rollout restart deployment/$service -n $NAMESPACE || \
        error_exit "Failed to restart $service"
    
    kubectl rollout status deployment/$service -n $NAMESPACE --timeout=180s || \
        error_exit "Restart failed"
    
    log_info "$service restarted ✓"
}

# Update backend
update_backend() {
    local version=${1:-$(get_next_version backend)}
    log_info "Updating backend to $version"
    build_and_push "backend" "$version" "backend"
    update_deployment "backend" "$version"
}

# Update frontend
update_frontend() {
    local version=${1:-$(get_next_version frontend)}
    log_info "Updating frontend to $version"
    build_and_push "frontend" "$version" "frontend"
    update_deployment "frontend" "$version"
}

# Update recommendation
update_recommendation() {
    local version=${1:-$(get_next_version recommendation)}
    log_info "Updating recommendation service to $version"
    build_and_push "recommendation" "$version" "recomendation"
    update_deployment "recommendation" "$version"
}

# Update nginx
update_nginx() {
    log_info "Restarting nginx (ensure configmap is updated first)"
    kubectl apply -f k8s/nginx/configmap.yaml || log_warn "ConfigMap not updated"
    restart_deployment "nginx"
}

# Update all services
update_all() {
    log_info "Updating all application services..."
    update_backend "$1"
    update_frontend "$1"
    update_recommendation "$1"
}

# Main execution
main() {
    if [ $# -lt 1 ]; then
        show_usage
        exit 1
    fi
    
    SERVICE=$1
    VERSION=${2:-""}
    
    echo ""
    log_step "Service Update Tool"
    echo ""
    
    # Check kubectl access
    kubectl cluster-info >/dev/null 2>&1 || \
        error_exit "Cannot connect to cluster. Run: gcloud container clusters get-credentials shop-app-cluster --region=europe-north1"
    
    case $SERVICE in
        backend)
            update_backend "$VERSION"
            ;;
        frontend)
            update_frontend "$VERSION"
            ;;
        recommendation|recomm|rec)
            update_recommendation "$VERSION"
            ;;
        nginx)
            update_nginx
            ;;
        grafana)
            restart_deployment "grafana"
            ;;
        prometheus|prom)
            restart_deployment "prometheus"
            ;;
        all)
            update_all "$VERSION"
            ;;
        -h|--help|help)
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown service: $SERVICE"
            echo ""
            show_usage
            exit 1
            ;;
    esac
    
    echo ""
    log_info "Update complete! ✓"
    echo ""
    log_info "View updated service:"
    echo "  kubectl get pods -n $NAMESPACE"
    echo "  kubectl logs -f deployment/$SERVICE -n $NAMESPACE"
    echo ""
}

main "$@"
