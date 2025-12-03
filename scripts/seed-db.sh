#!/bin/bash
# Database Seeding Script
# Seeds the MySQL database with realistic test data

set -euo pipefail

# Configuration
NAMESPACE="${NAMESPACE:-shop-app}"
NUM_USERS="${NUM_USERS:-100}"

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

# Check if backend pod is running
check_backend() {
    log_step "Checking backend pod status..."
    
    if ! kubectl get deployment backend -n $NAMESPACE >/dev/null 2>&1; then
        error_exit "Backend deployment not found. Deploy the application first."
    fi
    
    BACKEND_READY=$(kubectl get deployment backend -n $NAMESPACE -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
    if [ -z "$BACKEND_READY" ] || [ "$BACKEND_READY" -eq 0 ]; then
        error_exit "Backend pod is not ready. Wait for deployment to complete."
    fi
    
    log_info "Backend is ready ✓"
}

# Check if MySQL is ready
check_mysql() {
    log_step "Checking MySQL status..."
    
    if ! kubectl get deployment mysql -n $NAMESPACE >/dev/null 2>&1; then
        error_exit "MySQL deployment not found. Deploy the application first."
    fi
    
    MYSQL_READY=$(kubectl get deployment mysql -n $NAMESPACE -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
    if [ -z "$MYSQL_READY" ] || [ "$MYSQL_READY" -eq 0 ]; then
        error_exit "MySQL pod is not ready. Wait for deployment to complete."
    fi
    
    log_info "MySQL is ready ✓"
}

# Run seeding script
seed_database() {
    log_step "Seeding database with $NUM_USERS users..."
    
    log_info "This will create:"
    echo "  - $(($NUM_USERS + 1)) users (1 admin + $NUM_USERS customers)"
    echo "  - ~180 products"
    echo "  - ~157 orders with realistic behavior"
    echo ""
    
    log_info "Executing seed script in backend pod..."
    kubectl exec -n $NAMESPACE deployment/backend -- \
        python seed_mysql.py --users $NUM_USERS || \
        error_exit "Seeding failed"
    
    log_info "Database seeded successfully ✓"
}

# Verify seeding
verify_data() {
    log_step "Verifying seeded data..."
    
    # Count users
    USERS=$(kubectl exec -n $NAMESPACE deployment/mysql -- \
        mysql -udat515user -padmin123 DAT515 -sN -e "SELECT COUNT(*) FROM users" 2>/dev/null)
    
    # Count products
    PRODUCTS=$(kubectl exec -n $NAMESPACE deployment/mysql -- \
        mysql -udat515user -padmin123 DAT515 -sN -e "SELECT COUNT(*) FROM product" 2>/dev/null)
    
    # Count orders
    ORDERS=$(kubectl exec -n $NAMESPACE deployment/mysql -- \
        mysql -udat515user -padmin123 DAT515 -sN -e "SELECT COUNT(*) FROM orders" 2>/dev/null)
    
    echo ""
    log_info "Database Statistics:"
    echo "  👥 Users:    $USERS"
    echo "  📦 Products: $PRODUCTS"
    echo "  🛒 Orders:   $ORDERS"
    echo ""
}

# Print credentials
print_credentials() {
    log_step "Test Account Credentials:"
    echo ""
    echo "Admin Account:"
    echo "  Email:    admin@shop.com"
    echo "  Password: admin123"
    echo ""
    echo "Customer Account:"
    echo "  Email:    customer_1@example.com"
    echo "  Password: password123"
    echo ""
    echo "Additional customers: customer_2@example.com ... customer_${NUM_USERS}@example.com"
    echo "All customer passwords: password123"
    echo ""
}

# Main execution
main() {
    echo ""
    log_step "Starting Database Seeding..."
    echo ""
    
    check_backend
    check_mysql
    seed_database
    verify_data
    print_credentials
    
    log_info "Seeding complete! ✓"
    echo ""
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --users)
            NUM_USERS="$2"
            shift 2
            ;;
        --namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --users NUM       Number of customer users to create (default: 100)"
            echo "  --namespace NAME  Kubernetes namespace (default: shop-app)"
            echo "  -h, --help        Show this help message"
            echo ""
            echo "Example:"
            echo "  $0 --users 50"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

main "$@"
