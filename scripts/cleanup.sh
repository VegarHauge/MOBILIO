#!/bin/bash
# Cleanup Script - Delete all resources from GKE

set -euo pipefail

NAMESPACE="${NAMESPACE:-shop-app}"
PROJECT_ID="${GCP_PROJECT_ID:-dat515-478210}"
REGION="${GCP_REGION:-europe-north1}"
CLUSTER_NAME="shop-app-cluster"

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo ""
log_warn "╔════════════════════════════════════════════════════════════════╗"
log_warn "║                     CLEANUP WARNING                            ║"
log_warn "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "This will DELETE:"
echo "  - All deployments in namespace: $NAMESPACE"
echo "  - All services (including LoadBalancer)"
echo "  - All persistent volumes (DATABASE DATA WILL BE LOST)"
echo "  - All ConfigMaps and Secrets"
echo ""
log_warn "To delete the entire cluster, add --delete-cluster flag"
echo ""

read -p "Are you sure you want to continue? (type 'yes' to confirm): " confirm

if [ "$confirm" != "yes" ]; then
    log_info "Cleanup cancelled"
    exit 0
fi

# Delete namespace (this deletes everything in it)
log_info "Deleting namespace: $NAMESPACE"
kubectl delete namespace $NAMESPACE --timeout=180s || log_warn "Namespace deletion failed or already deleted"

log_info "Resources deleted successfully ✓"

# Check if --delete-cluster flag is provided
if [[ " $@ " =~ " --delete-cluster " ]]; then
    echo ""
    log_warn "Deleting entire GKE cluster: $CLUSTER_NAME"
    read -p "Type 'DELETE' to confirm cluster deletion: " confirm_cluster
    
    if [ "$confirm_cluster" != "DELETE" ]; then
        log_info "Cluster deletion cancelled"
        exit 0
    fi
    
    log_info "Deleting cluster..."
    gcloud container clusters delete $CLUSTER_NAME \
        --region=$REGION \
        --quiet || log_error "Cluster deletion failed"
    
    log_info "Cluster deleted ✓"
fi

echo ""
log_info "Cleanup complete!"
echo ""
