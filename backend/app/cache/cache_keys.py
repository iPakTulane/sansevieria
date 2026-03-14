class CacheKeys:
    PRODUCTS_CATALOG = "products:catalog"
    
    @staticmethod
    def get_product_key(product_id: int) -> str:
        return f"products:detail:{product_id}"
