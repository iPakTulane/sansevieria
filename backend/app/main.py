from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth_router, product_router, cart_router, order_router

# Create database tables (now managed by Alembic)
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sansevieria Backend API",
    description="Foundational backend for Sansevieria Web Application",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/api/auth", tags=["auth"])
app.include_router(product_router.router, prefix="/api/products", tags=["products"])
app.include_router(cart_router.router, prefix="/api/cart", tags=["cart"])
app.include_router(order_router.checkout_router, prefix="/api/checkout", tags=["checkout"])
app.include_router(order_router.order_router, prefix="/api/orders", tags=["orders"])

from app.messaging.rabbitmq import setup_queues

@app.on_event("startup")
def startup_event():
    setup_queues()

@app.get("/health")
def health_check():
    return {"status": "ok"}
