from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    title: str
    description: Optional[str] = None
    size: Optional[str] = None
    light_level: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    category: Optional[str] = None

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    size: Optional[str] = None
    light_level: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    category: Optional[str] = None

class ProductResponse(ProductBase):
    id: int
    
    class Config:
        from_attributes = True
