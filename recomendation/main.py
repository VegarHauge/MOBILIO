from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from services.ml_recommendation_service import MLRecommendationService
from models.schemas import ProductRecommendation
import os

app = FastAPI(
    title="ML Product Recommendation API", 
    version="2.0.0",
    description="Streamlined ML-powered recommendation system with focused, robust features",
    root_path="/api"
)

# Add CORS middleware to allow cross-origin requests from anywhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Database configuration
PRODUCTION_DB_URL = os.getenv("DATABASE_URL", "test.db")
ANALYTICS_DB_URL = os.getenv("ANALYTICS_DB_URL", "analytics.db")

def get_ml_service():
    return MLRecommendationService(PRODUCTION_DB_URL, ANALYTICS_DB_URL)

# ===== CORE RECOMMENDATION ENDPOINTS =====

@app.get("/similar/{product_id}", response_model=List[ProductRecommendation])
async def get_similar_products(
    product_id: int,
    limit: int = 10,
    service: MLRecommendationService = Depends(get_ml_service)
):
    """
    Get products similar to the given product using ML similarity analysis.
    Based on product features like category, brand, price, and rating.
    """
    if limit > 50:
        raise HTTPException(status_code=400, detail="Limit cannot exceed 50")
    
    try:
        recommendations = service.get_similar_products(product_id, limit)
        if not recommendations:
            raise HTTPException(status_code=404, detail=f"No similar products found for product {product_id}")
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting similar products: {str(e)}")

@app.get("/copurchase/{product_id}", response_model=List[ProductRecommendation])
async def get_copurchase_recommendations(
    product_id: int,
    limit: int = 10,
    service: MLRecommendationService = Depends(get_ml_service)
):
    """
    Get products frequently bought together with the given product.
    Based on ML analysis of purchase patterns and co-occurrence data.
    """
    if limit > 50:
        raise HTTPException(status_code=400, detail="Limit cannot exceed 50")
    
    try:
        recommendations = service.get_copurchase_recommendations(product_id, limit)
        if not recommendations:
            raise HTTPException(status_code=404, detail=f"No co-purchase recommendations found for product {product_id}")
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting co-purchase recommendations: {str(e)}")

# ===== TRAINING AND DATA MANAGEMENT =====

@app.post("/train")
async def train_models(
    service: MLRecommendationService = Depends(get_ml_service)
) -> Dict[str, Any]:
    """
    Train ML recommendation models using current data.
    This will build similarity matrices and co-purchase patterns.
    """
    try:
        result = service.train_models()
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

@app.post("/sync-data")
async def sync_production_data(
    service: MLRecommendationService = Depends(get_ml_service)
) -> Dict[str, Any]:
    """
    Sync data from production database to analytics database for ML training.
    Run this before training models to ensure you have the latest data.
    """
    try:
        result = service.sync_production_data()
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data sync failed: {str(e)}")

@app.post("/full-retrain")
async def full_retrain(
    service: MLRecommendationService = Depends(get_ml_service)
) -> Dict[str, Any]:
    """
    Complete retraining workflow: sync data from production, then train models.
    This is the easiest way to update your ML models with fresh data.
    """
    try:
        # First sync data
        sync_result = service.sync_production_data()
        if sync_result["status"] == "error":
            raise HTTPException(status_code=500, detail=f"Data sync failed: {sync_result['error']}")
        
        # Then train models
        train_result = service.train_models()
        if train_result["status"] == "error":
            raise HTTPException(status_code=500, detail=f"Training failed: {train_result['error']}")
        
        return {
            "status": "success",
            "sync_result": sync_result,
            "training_result": train_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Full retrain failed: {str(e)}")

# ===== HEALTH AND STATUS =====

@app.get("/health")
async def health_check(
    service: MLRecommendationService = Depends(get_ml_service)
) -> Dict[str, Any]:
    """
    Get system health status, model information, and performance metrics.
    """
    try:
        return service.get_health_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/")
async def root():
    """
    API information and quick start guide.
    """
    return {
        "service": "ML Product Recommendation API",
        "version": "2.0.0",
        "description": "Streamlined ML-powered recommendation system",
        "core_endpoints": {
            "/similar/{product_id}": "Get ML-powered similar products",
            "/copurchase/{product_id}": "Get products frequently bought together",
            "/train": "Train ML models",
            "/sync-data": "Sync production data",
            "/full-retrain": "Complete retrain workflow",
            "/health": "System health and status"
        },
        "docs": "/docs",
        "quick_start": [
            "1. POST /sync-data - Sync latest data from production",
            "2. POST /train - Train ML models",
            "3. GET /similar/{product_id} - Get recommendations",
            "4. GET /health - Check system status"
        ]
    }

# ===== UTILITY ENDPOINTS =====

@app.get("/models/info")
async def get_model_info(
    service: MLRecommendationService = Depends(get_ml_service)
) -> Dict[str, Any]:
    """
    Get detailed information about trained models and their performance.
    """
    try:
        health = service.get_health_status()
        return {
            "models_trained": health.get("models_trained", False),
            "model_files": health.get("model_files", {}),
            "statistics": health.get("model_statistics", {}),
            "last_updated": health.get("timestamp")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model info: {str(e)}")