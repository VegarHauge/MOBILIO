# backend/core/metrics.py
from fastapi import Request
from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator

# Define custom Prometheus counter
product_requests = Counter(
    "product_requests_total",
    "Total number of product API requests"
)

# Middleware to count /api/products hits
async def count_product_requests_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/products"):
        product_requests.inc()
    response = await call_next(request)
    return response


# Function to attach Prometheus instrumentation
def setup_metrics(app):
    # Register our custom counter middleware
    app.middleware("http")(count_product_requests_middleware)
    # Use FastAPI Instrumentator for automatic metrics
    Instrumentator().instrument(app).expose(app)
