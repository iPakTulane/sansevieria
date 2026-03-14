from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.product_schema import ProductResponse, ProductBase
from app.services.product_service import get_products, get_product
from app.models.product import Product
from app.cache.cache_service import CacheService
from app.cache.cache_keys import CacheKeys

router = APIRouter()

@router.get("/", response_model=List[ProductResponse])
def read_products(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    cache_key = CacheKeys.PRODUCTS_CATALOG
    
    # 2. Check Redis
    cached_products = CacheService.get_cache(cache_key)
    if cached_products:
        return cached_products
        
    # 4. If not cached -> query PostgreSQL
    products = get_products(db, skip=skip, limit=limit)
    
    # 5. Store result in Redis
    # Serialize to dicts for caching
    serialized = [ProductResponse.from_orm(p).dict() for p in products]
    CacheService.set_cache(cache_key, serialized, ttl=300)
    
    return products

@router.get("/{product_id}", response_model=ProductResponse)
def read_product(product_id: int, db: Session = Depends(get_db)):
    cache_key = CacheKeys.get_product_key(product_id)
    
    cached_product = CacheService.get_cache(cache_key)
    if cached_product:
        return cached_product
        
    db_product = get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
        
    serialized = ProductResponse.from_orm(db_product).dict()
    CacheService.set_cache(cache_key, serialized, ttl=300)
    
    return db_product

@router.post("/", response_model=ProductResponse)
def create_product(product: ProductBase, db: Session = Depends(get_db)):
    """Mock endpoint to demonstrate cache invalidation"""
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # Invalidate catalog cache since underlying data changed
    CacheService.invalidate_cache(CacheKeys.PRODUCTS_CATALOG)
    
    return db_product
