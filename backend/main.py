from fastapi import FastAPI
from api.products import router as products_router
from api.cart import router as cart_router
import uvicorn
from api.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from api.orders import router as orders_router
from api.payment import router as payment_router
from api.health import router as health_router
#from api.admin import router as admin_router
from core.config import settings, get_cors_config
from core.metrics import setup_metrics

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS from settings
cors_config = get_cors_config()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config["allow_origins"],
    allow_credentials=cors_config["allow_credentials"],
    allow_methods=cors_config["allow_methods"],
    allow_headers=cors_config["allow_headers"],
)

app.include_router(products_router, prefix="/api")
app.include_router(cart_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(orders_router, prefix="/api")
app.include_router(payment_router, prefix="/api")
app.include_router(health_router, prefix="/api")
#app.include_router(admin_router)

setup_metrics(app)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)