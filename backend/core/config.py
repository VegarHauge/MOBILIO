"""
Configuration Management

This module handles all environment variables and application configuration.
Uses pydantic-settings for validation and type safety.

Environment variables are loaded from:
1. .env file (local development)
2. System environment variables (production)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "E-Commerce Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./test.db"
    
    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-here-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Settings
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "*"
    CORS_ALLOW_HEADERS: str = "*"
    
    # Stripe Configuration (Optional - for payment integration)
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # Frontend Configuration
    FRONTEND_URL: str = "http://localhost:3000"
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Admin User Default Credentials
    ADMIN_EMAIL: str = "admin@shopify.com"
    ADMIN_PASSWORD: str = "admin123"
    ADMIN_NAME: str = "System Administrator"
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # File Upload (if you add this feature)
    MAX_UPLOAD_SIZE: int = 5242880  # 5MB in bytes
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,gif"
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: Optional[str] = None
    S3_BUCKET_NAME: Optional[str] = None
    
    # Security
    PASSWORD_MIN_LENGTH: int = 8
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Argon2 Configuration (password hashing)
    ARGON2_MEMORY_COST: int = 65536  # 64 MB
    ARGON2_TIME_COST: int = 3  # 3 iterations
    ARGON2_PARALLELISM: int = 1  # 1 thread
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields in .env
    )
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Convert CORS_ORIGINS string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def cors_methods_list(self) -> list[str]:
        """Convert CORS_ALLOW_METHODS string to list"""
        if self.CORS_ALLOW_METHODS == "*":
            return ["*"]
        return [method.strip() for method in self.CORS_ALLOW_METHODS.split(",")]
    
    @property
    def cors_headers_list(self) -> list[str]:
        """Convert CORS_ALLOW_HEADERS string to list"""
        if self.CORS_ALLOW_HEADERS == "*":
            return ["*"]
        return [header.strip() for header in self.CORS_ALLOW_HEADERS.split(",")]
    
    @property
    def allowed_extensions_list(self) -> list[str]:
        """Convert ALLOWED_EXTENSIONS string to list"""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return not self.DEBUG
    
    @property
    def database_echo(self) -> bool:
        """Enable SQL logging in debug mode"""
        return self.DEBUG
    
    def validate_production_config(self) -> list[str]:
        """Validate that production-critical settings are properly configured"""
        errors = []
        
        if self.is_production:
            if self.SECRET_KEY == "your-secret-key-here-change-this-in-production":
                errors.append("SECRET_KEY must be changed in production!")
            
            if len(self.SECRET_KEY) < 32:
                errors.append("SECRET_KEY should be at least 32 characters long!")
            
            if self.ADMIN_PASSWORD == "admin123":
                errors.append("ADMIN_PASSWORD must be changed in production!")
        
        return errors


# Create a global settings instance
settings = Settings()

# Validate production configuration on startup
if settings.is_production:
    config_errors = settings.validate_production_config()
    if config_errors:
        print("⚠️  PRODUCTION CONFIGURATION WARNINGS:")
        for error in config_errors:
            print(f"   - {error}")
        print()


# Helper functions for common configuration access
def get_database_url() -> str:
    """Get the database connection URL"""
    return settings.DATABASE_URL


def get_jwt_config() -> dict:
    """Get JWT configuration as a dictionary"""
    return {
        "secret_key": settings.SECRET_KEY,
        "algorithm": settings.ALGORITHM,
        "access_token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES
    }


def get_cors_config() -> dict:
    """Get CORS configuration as a dictionary"""
    return {
        "allow_origins": settings.cors_origins_list,
        "allow_credentials": settings.CORS_ALLOW_CREDENTIALS,
        "allow_methods": settings.cors_methods_list,
        "allow_headers": settings.cors_headers_list
    }


def get_argon2_config() -> dict:
    """Get Argon2 password hashing configuration"""
    return {
        "memory_cost": settings.ARGON2_MEMORY_COST,
        "time_cost": settings.ARGON2_TIME_COST,
        "parallelism": settings.ARGON2_PARALLELISM
    }


# Display configuration summary (only in debug mode)
if settings.DEBUG:
    print("Configuration Loaded:")
    print(f"   App: {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"   Database: {settings.DATABASE_URL}")
    print(f"   Debug Mode: {settings.DEBUG}")
    print(f"   CORS Origins: {', '.join(settings.cors_origins_list)}")
    print(f"   JWT Expiration: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
    if settings.STRIPE_SECRET_KEY:
        print("   Stripe: Configured")
    print()
