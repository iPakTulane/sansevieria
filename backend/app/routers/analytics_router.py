from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.database import get_db
from app.routers.auth_router import require_analytics_user
from app.models.user import User
from app.schemas.analytics_schema import (
    SalesSummaryResponse,
    SalesTrendResponse,
    ProductPerformanceResponse,
)
from app.services.analytics_service import (
    get_sales_summary,
    get_sales_trend,
    get_product_performance,
)


router = APIRouter()


@router.get("/sales/summary", response_model=SalesSummaryResponse)
def read_sales_summary(
    current_user: User = Depends(require_analytics_user),
    db: Session = Depends(get_db),
):
    try:
        return get_sales_summary(db)
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Analytics data is temporarily unavailable",
        )


@router.get("/sales/trend", response_model=SalesTrendResponse)
def read_sales_trend(
    current_user: User = Depends(require_analytics_user),
    db: Session = Depends(get_db),
):
    try:
        return SalesTrendResponse(items=get_sales_trend(db))
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Analytics data is temporarily unavailable",
        )


@router.get("/products/performance", response_model=ProductPerformanceResponse)
def read_product_performance(
    current_user: User = Depends(require_analytics_user),
    db: Session = Depends(get_db),
):
    try:
        return ProductPerformanceResponse(items=get_product_performance(db))
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Analytics data is temporarily unavailable",
        )
