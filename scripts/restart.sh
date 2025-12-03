#!/bin/bash
# Quick Restart Script - Restart services without rebuilding
# Use this when you only need to restart a pod (no code changes)

set -euo pipefail

NAMESPACE="shop-app"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

show_usage() {
    echo "Usage: $0 <service>"
    echo ""
    echo "Quick restart without rebuilding images"
    echo ""
    echo "Services:"
    echo "  backend, frontend, recommendation, nginx, grafana, prometheus"
    echo "  mysql, analyticsdb, redis"
    echo "  all - restart all deployments"
    echo ""
    echo "Examples:"
    echo "  $0 backend     # Restart backend pods"
    echo "  $0 nginx       # Restart nginx (useful after config changes)"
    echo "  $0 all         # Restart everything"
}

restart() {
    local service=$1
    log_step "Restarting $service..."
    kubectl rollout restart deployment/$service -n $NAMESPACE
    kubectl rollout status deployment/$service -n $NAMESPACE --timeout=180s
    log_info "$service restarted ✓"
}

main() {
    if [ $# -lt 1 ]; then
        show_usage
        exit 1
    fi
    
    SERVICE=$1
    
    case $SERVICE in
        all)
            log_info "Restarting all deployments..."
            kubectl rollout restart deployment --all -n $NAMESPACE
            ;;
        backend|frontend|recommendation|nginx|grafana|prometheus|mysql|analyticsdb|redis)
            restart "$SERVICE"
            ;;
        *)
            echo "Unknown service: $SERVICE"
            show_usage
            exit 1
            ;;
    esac
    
    echo ""
    log_info "Done! ✓"
}

main "$@"
