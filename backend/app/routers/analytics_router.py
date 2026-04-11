from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.routers.auth_router import get_current_user
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Authenticated access only. There is currently no admin-role model in the project.
    return get_sales_summary(db)


@router.get("/sales/trend", response_model=SalesTrendResponse)
def read_sales_trend(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return SalesTrendResponse(items=get_sales_trend(db))


@router.get("/products/performance", response_model=ProductPerformanceResponse)
def read_product_performance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ProductPerformanceResponse(items=get_product_performance(db))
