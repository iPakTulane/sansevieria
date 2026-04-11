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
from app.utils.logger import get_logger


router = APIRouter()
logger = get_logger("ANALYTICS_API")


@router.get("/sales/summary", response_model=SalesSummaryResponse)
def read_sales_summary(
    current_user: User = Depends(require_analytics_user),
    db: Session = Depends(get_db),
):
    # Router stays thin: auth, logging, and safe error mapping around read-only service call.
    try:
        logger.info(
            "analytics",
            "sales_summary",
            "Analytics endpoint called",
            endpoint="/api/analytics/sales/summary",
            user_id=current_user.id,
            user_email=current_user.email,
        )
        return get_sales_summary(db)
    except SQLAlchemyError as e:
        logger.error(
            "analytics",
            "sales_summary",
            "Analytics endpoint failed",
            endpoint="/api/analytics/sales/summary",
            user_id=current_user.id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Analytics data is temporarily unavailable",
        )
    except Exception as e:
        logger.error(
            "analytics",
            "sales_summary",
            "Unhandled analytics endpoint error",
            endpoint="/api/analytics/sales/summary",
            user_id=current_user.id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected analytics error",
        )


@router.get("/sales/trend", response_model=SalesTrendResponse)
def read_sales_trend(
    current_user: User = Depends(require_analytics_user),
    db: Session = Depends(get_db),
):
    try:
        items = get_sales_trend(db)
        logger.info(
            "analytics",
            "sales_trend",
            "Analytics endpoint called",
            endpoint="/api/analytics/sales/trend",
            user_id=current_user.id,
            user_email=current_user.email,
            result_count=len(items),
        )
        return SalesTrendResponse(items=items)
    except SQLAlchemyError as e:
        logger.error(
            "analytics",
            "sales_trend",
            "Analytics endpoint failed",
            endpoint="/api/analytics/sales/trend",
            user_id=current_user.id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Analytics data is temporarily unavailable",
        )
    except Exception as e:
        logger.error(
            "analytics",
            "sales_trend",
            "Unhandled analytics endpoint error",
            endpoint="/api/analytics/sales/trend",
            user_id=current_user.id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected analytics error",
        )


@router.get("/products/performance", response_model=ProductPerformanceResponse)
def read_product_performance(
    current_user: User = Depends(require_analytics_user),
    db: Session = Depends(get_db),
):
    try:
        items = get_product_performance(db)
        logger.info(
            "analytics",
            "products_performance",
            "Analytics endpoint called",
            endpoint="/api/analytics/products/performance",
            user_id=current_user.id,
            user_email=current_user.email,
            result_count=len(items),
        )
        return ProductPerformanceResponse(items=items)
    except SQLAlchemyError as e:
        logger.error(
            "analytics",
            "products_performance",
            "Analytics endpoint failed",
            endpoint="/api/analytics/products/performance",
            user_id=current_user.id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Analytics data is temporarily unavailable",
        )
    except Exception as e:
        logger.error(
            "analytics",
            "products_performance",
            "Unhandled analytics endpoint error",
            endpoint="/api/analytics/products/performance",
            user_id=current_user.id,
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected analytics error",
        )
