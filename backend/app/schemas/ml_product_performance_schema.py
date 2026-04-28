from pydantic import BaseModel
from typing import List


class MLProductPerformanceItem(BaseModel):
    product_id: int
    product_title: str
    product_category: str | None = None
    units_sold: int
    revenue: float
    orders_count: int
    performance_class: str
    confidence: float | None = None
    explanation: str


class MLProductPerformanceResponse(BaseModel):
    items: List[MLProductPerformanceItem]
