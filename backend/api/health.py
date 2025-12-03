"""
Health Check API Endpoints

Provides endpoints for monitoring backend health:
- /health - Basic health check (fast, for load balancers)
- /health/detailed - Comprehensive health check (slower, for monitoring)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.deps import get_db
from services.health_service import HealthService
from typing import Dict, Any

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
def get_basic_health() -> Dict[str, Any]:
    """
    Basic health check endpoint
    
    Returns simple status indicating API is reachable.
    Suitable for:
    - Load balancer health checks
    - Uptime monitoring
    - Quick status verification
    
    Returns 200 if API is running.
    """
    return HealthService.get_basic_health()


@router.get("/detailed")
def get_detailed_health(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Comprehensive health check endpoint
    
    Checks status of all backend components:
    - Database connectivity and response time
    - S3 bucket accessibility
    - Stripe API connectivity
    - Overall system status
    
    Status values:
    - healthy: All systems operational
    - degraded: Some non-critical services unavailable
    - unhealthy: Critical services (database) unavailable
    
    Use this for:
    - Detailed monitoring dashboards
    - Troubleshooting
    - Service status pages
    """
    return HealthService.get_comprehensive_health(db)


@router.get("/database")
def get_database_health(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Check database connectivity only
    
    Returns database connection status and response time.
    """
    return HealthService.check_database(db)


@router.get("/s3")
def get_s3_health() -> Dict[str, Any]:
    """
    Check S3 bucket accessibility only
    
    Returns S3 bucket status and accessibility.
    """
    return HealthService.check_s3()


@router.get("/stripe")
def get_stripe_health() -> Dict[str, Any]:
    """
    Check Stripe API connectivity only
    
    Returns Stripe API status and account information.
    """
    return HealthService.check_stripe()
