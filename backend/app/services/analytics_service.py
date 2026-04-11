from sqlalchemy import text
from sqlalchemy.orm import Session
from app.schemas.analytics_schema import (
    SalesSummaryResponse,
    SalesTrendItem,
    ProductPerformanceItem,
)


def _to_float(value) -> float:
    if value is None:
        return 0.0
    return float(value)


def _to_int(value) -> int:
    if value is None:
        return 0
    return int(value)


def get_sales_summary(db: Session) -> SalesSummaryResponse:
    row = db.execute(
        text(
            """
            SELECT
                total_revenue,
                completed_orders,
                pending_orders,
                failed_orders,
                avg_order_value,
                total_units_sold
            FROM sales_summary_view
            """
        )
    ).mappings().first()

    if not row:
        return SalesSummaryResponse(
            total_revenue=0.0,
            completed_orders=0,
            pending_orders=0,
            failed_orders=0,
            avg_order_value=0.0,
            total_units_sold=0,
        )

    return SalesSummaryResponse(
        total_revenue=_to_float(row["total_revenue"]),
        completed_orders=_to_int(row["completed_orders"]),
        pending_orders=_to_int(row["pending_orders"]),
        failed_orders=_to_int(row["failed_orders"]),
        avg_order_value=_to_float(row["avg_order_value"]),
        total_units_sold=_to_int(row["total_units_sold"]),
    )


def get_sales_trend(db: Session) -> list[SalesTrendItem]:
    rows = db.execute(
        text(
            """
            SELECT
                order_date,
                orders_count,
                units_sold,
                revenue
            FROM sales_over_time_view
            ORDER BY order_date
            """
        )
    ).mappings().all()

    return [
        SalesTrendItem(
            order_date=row["order_date"],
            orders_count=_to_int(row["orders_count"]),
            units_sold=_to_int(row["units_sold"]),
            revenue=_to_float(row["revenue"]),
        )
        for row in rows
    ]


def get_product_performance(db: Session) -> list[ProductPerformanceItem]:
    rows = db.execute(
        text(
            """
            SELECT
                product_id,
                product_title,
                product_category,
                units_sold,
                revenue,
                orders_count
            FROM product_performance_view
            ORDER BY revenue DESC, units_sold DESC, product_id
            """
        )
    ).mappings().all()

    return [
        ProductPerformanceItem(
            product_id=_to_int(row["product_id"]),
            product_title=row["product_title"],
            product_category=row["product_category"],
            units_sold=_to_int(row["units_sold"]),
            revenue=_to_float(row["revenue"]),
            orders_count=_to_int(row["orders_count"]),
        )
        for row in rows
    ]
