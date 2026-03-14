import random

def generate_order_id() -> str:
    """Generate a business identifier for orders like ORD-000123"""
    rand_num = random.randint(1000, 999999)
    return f"ORD-{rand_num:06d}"
