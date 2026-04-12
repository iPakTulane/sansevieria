from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from app.database import engine, Base
from app.config import settings
from app.routers import auth_router, product_router, cart_router, order_router, analytics_router, chat_router
from app.utils.logger import get_logger

# Create database tables (now managed by Alembic)
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sansevieria Backend API",
    description="Foundational backend for Sansevieria Web Application",
    version="1.0.0"
)
logger = get_logger("API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/api/auth", tags=["auth"])
app.include_router(product_router.router, prefix="/api/products", tags=["products"])
app.include_router(cart_router.router, prefix="/api/cart", tags=["cart"])
app.include_router(order_router.checkout_router, prefix="/api/checkout", tags=["checkout"])
app.include_router(order_router.order_router, prefix="/api/orders", tags=["orders"])
app.include_router(analytics_router.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(chat_router.router, prefix="/api/chat", tags=["chat"])

from app.messaging.rabbitmq import setup_queues

@app.on_event("startup")
def startup_event():
    logger.info(
        "system",
        "startup",
        "Application startup initiated",
        allowed_origins=",".join(settings.allowed_origins_list),
    )
    setup_queues()
    logger.info("system", "startup", "Application startup completed")

@app.get("/health")
def health_check(request: Request):
    logger.info(
        "health",
        "health",
        "Health check called",
        path=str(request.url.path),
        client_host=(request.client.host if request.client else "unknown"),
    )
    return {"status": "ok"}
