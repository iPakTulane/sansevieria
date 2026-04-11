from pydantic import BaseModel
from datetime import date
from typing import List


class SalesSummaryResponse(BaseModel):
    total_revenue: float
    completed_orders: int
    pending_orders: int
    failed_orders: int
    avg_order_value: float
    total_units_sold: int


class SalesTrendItem(BaseModel):
    order_date: date
    orders_count: int
    units_sold: int
    revenue: float


class SalesTrendResponse(BaseModel):
    items: List[SalesTrendItem]


class ProductPerformanceItem(BaseModel):
    product_id: int
    product_title: str
    product_category: str | None = None
    units_sold: int
    revenue: float
    orders_count: int


class ProductPerformanceResponse(BaseModel):
    items: List[ProductPerformanceItem]
