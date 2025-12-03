"""
Health Check Service

Monitors the health and status of various backend components:
- Database connectivity
- S3 bucket availability
- Stripe API connectivity
- System metrics
"""

import time
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from core.config import settings
from services.s3_service import s3_service
import stripe

logger = logging.getLogger(__name__)


class HealthService:
    """Service for checking health of backend components"""
    
    @staticmethod
    def check_database(db: Session) -> Dict[str, Any]:
        """
        Check database connectivity and performance
        
        Returns:
            Dictionary with status, response_time, and details
        """
        try:
            start_time = time.time()
            
            # Try a simple query
            result = db.execute(text("SELECT 1")).fetchone()
            
            response_time = round((time.time() - start_time) * 1000, 2)  # ms
            
            if result and result[0] == 1:
                return {
                    "status": "healthy",
                    "response_time_ms": response_time,
                    "database_url": settings.DATABASE_URL.split("://")[0] + "://***",  # Hide credentials
                    "message": "Database connection successful"
                }
            else:
                return {
                    "status": "unhealthy",
                    "response_time_ms": response_time,
                    "message": "Database query returned unexpected result"
                }
                
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}"
            }
    
    @staticmethod
    def check_s3() -> Dict[str, Any]:
        """
        Check S3 bucket accessibility
        
        Returns:
            Dictionary with status and details
        """
        try:
            start_time = time.time()
            
            if not s3_service.is_configured():
                return {
                    "status": "not_configured",
                    "message": "S3 credentials not configured"
                }
            
            # Try to list objects in the bucket (just check access, don't fetch all)
            s3_service.s3_client.head_bucket(Bucket=s3_service.bucket_name)
            
            response_time = round((time.time() - start_time) * 1000, 2)  # ms
            
            return {
                "status": "healthy",
                "response_time_ms": response_time,
                "bucket_name": s3_service.bucket_name,
                "region": settings.AWS_REGION,
                "message": "S3 bucket accessible"
            }
            
        except s3_service.s3_client.exceptions.NoSuchBucket:
            return {
                "status": "unhealthy",
                "message": f"S3 bucket '{s3_service.bucket_name}' does not exist"
            }
        except Exception as e:
            logger.error(f"S3 health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "message": f"S3 connection failed: {str(e)}"
            }
    
    @staticmethod
    def check_stripe() -> Dict[str, Any]:
        """
        Check Stripe API connectivity
        
        Returns:
            Dictionary with status and details
        """
        try:
            start_time = time.time()
            
            if not settings.STRIPE_SECRET_KEY:
                return {
                    "status": "not_configured",
                    "message": "Stripe API key not configured"
                }
            
            # Set the API key
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            # Try to retrieve account info (lightweight API call)
            account = stripe.Account.retrieve()
            
            response_time = round((time.time() - start_time) * 1000, 2)  # ms
            
            return {
                "status": "healthy",
                "response_time_ms": response_time,
                "account_id": account.id,
                "account_type": account.type,
                "charges_enabled": account.charges_enabled,
                "message": "Stripe API accessible"
            }
            
        except stripe.error.AuthenticationError as e:
            logger.error(f"Stripe authentication failed: {str(e)}")
            return {
                "status": "unhealthy",
                "message": "Stripe authentication failed - invalid API key"
            }
        except stripe.error.APIConnectionError as e:
            logger.error(f"Stripe connection failed: {str(e)}")
            return {
                "status": "unhealthy",
                "message": "Cannot connect to Stripe API"
            }
        except Exception as e:
            logger.error(f"Stripe health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "message": f"Stripe check failed: {str(e)}"
            }
    
    @staticmethod
    def get_comprehensive_health(db: Session) -> Dict[str, Any]:
        """
        Get comprehensive health check of all services
        
        Returns:
            Dictionary with overall status and component statuses
        """
        start_time = time.time()
        
        # Check all components
        db_health = HealthService.check_database(db)
        s3_health = HealthService.check_s3()
        stripe_health = HealthService.check_stripe()
        
        # Determine overall status
        component_statuses = [
            db_health.get("status"),
            s3_health.get("status"),
            stripe_health.get("status")
        ]
        
        # Overall is unhealthy if any critical component is unhealthy
        # Database is critical, S3 and Stripe can be "not_configured" in dev
        if db_health.get("status") == "unhealthy":
            overall_status = "unhealthy"
        elif "unhealthy" in component_statuses:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        total_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            "status": overall_status,
            "timestamp": time.time(),
            "total_response_time_ms": total_time,
            "application": {
                "name": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "environment": "production" if settings.is_production else "development"
            },
            "components": {
                "database": db_health,
                "s3": s3_health,
                "stripe": stripe_health
            }
        }
    
    @staticmethod
    def get_basic_health() -> Dict[str, Any]:
        """
        Get basic health check (just API reachability)
        Useful for simple uptime monitoring
        
        Returns:
            Dictionary with basic status
        """
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "application": {
                "name": settings.APP_NAME,
                "version": settings.APP_VERSION
            },
            "message": "API is reachable"
        }
