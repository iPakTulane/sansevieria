import logging
import random
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.utils.security import get_password_hash

logger = logging.getLogger(__name__)

RANDOM_SEED = 20260411
HISTORICAL_DAYS = 180
HISTORICAL_ORDER_COUNT = 320
HISTORICAL_USER_COUNT = 18
MOCK_ORDER_PREFIX = "MOCK-"

def seed_data(db: Session):
    # Seed User
    test_email = "test@example.com"
    user = db.query(User).filter(User.email == test_email).first()
    if not user:
        new_user = User(
            name="Test User",
            email=test_email,
            password_hash=get_password_hash("password123")
        )
        db.add(new_user)
        logger.info(f"Seeded user: {test_email}")

    # Diverse Array of Seed Products using fully authenticated high-availability Unsplash links
    products_to_seed = [
        {
            "title": "Sansevieria Trifasciata 'Zeylanica'",
            "description": "The classic Snake Plant, known for its tall, upright leaves with distinctive wavy horizontal bands.",
            "size": "Medium",
            "light_level": "Low to Bright Indirect",
            "price": 25.00,
            "image_url": "https://images.unsplash.com/photo-1547516508-e910d368d995?auto=format&fit=crop&w=800&q=80",
            "category": "Classic"
        },
        {
            "title": "Sansevieria Cylindrica",
            "description": "Features round, cylindrical leaves that grow outward like a fan. Highly architectural and striking.",
            "size": "Small",
            "light_level": "Medium to Bright Indirect",
            "price": 30.00,
            "image_url": "https://images.unsplash.com/photo-1599009944997-3544a939813c?auto=format&fit=crop&w=800&q=80",
            "category": "Rare"
        },
        {
            "title": "Sansevieria 'Moonshine'",
            "description": "Broad, silvery-green leaves that bring a subtle, almost glowing lunar brightness to any room.",
            "size": "Medium",
            "light_level": "Low to Medium Indirect",
            "price": 28.00,
            "image_url": "https://images.unsplash.com/photo-1593482892540-73c9199d8949?auto=format&fit=crop&w=800&q=80",
            "category": "Modern"
        },
        {
            "title": "Sansevieria Trifasciata 'Hahnii'",
            "description": "A dwarf cultivar commonly called the Bird's Nest Snake Plant. Perfect for countertops and desktops.",
            "size": "Mini",
            "light_level": "Low to Medium",
            "price": 18.00,
            "image_url": "https://images.unsplash.com/photo-1613498630970-f2a333cb4974?auto=format&fit=crop&w=800&q=80",
            "category": "Classic"
        },
        {
            "title": "Sansevieria Masoniana",
            "description": "Known as the Whale Fin Sansevieria because of its distinctly massive, wide, mottled singular leaf.",
            "size": "Large",
            "light_level": "Bright Indirect",
            "price": 45.00,
            "image_url": "https://images.unsplash.com/photo-1616961002389-504228edfcb7?auto=format&fit=crop&w=800&q=80",
            "category": "Rare"
        },
        {
            "title": "Sansevieria Bantel's Sensation",
            "description": "Distinctive white vertical striping on thin, dark green leaves. An elegant, towering showpiece.",
            "size": "Medium",
            "light_level": "Bright Indirect",
            "price": 38.00,
            "image_url": "https://images.unsplash.com/photo-1616961065849-edf307a08bcb?auto=format&fit=crop&w=800&q=80", 
            "category": "Modern"
        },
        {
            "title": "Sansevieria Trifasciata 'Lauren'",
            "description": "Vibrant yellow banding on the margins bordering deep emerald. Brighter than the typical Laurentii.",
            "size": "Medium",
            "light_level": "Medium Indirect",
            "price": 26.00,
            "image_url": "https://images.unsplash.com/photo-1641789570360-370eaeac713e?auto=format&fit=crop&w=800&q=80",
            "category": "Classic"
        },
        {
            "title": "Sansevieria Ehrenbergii 'Samurai'",
            "description": "Features thick, V-shaped channeled leaves that stack gracefully on top of one another.",
            "size": "Small",
            "light_level": "Bright Indirect",
            "price": 55.00,
            "image_url": "images/samurai.png", # Fully resolved with custom AI rendering
            "category": "Rare"
        },
        {
            "title": "Sansevieria Trifasciata 'Golden Hahnii'",
            "description": "A dwarf bird's nest variety highlighted by intense, bright golden yellow striped foliage.",
            "size": "Mini",
            "light_level": "Low Indirect",
            "price": 22.00,
            "image_url": "https://images.unsplash.com/photo-1658309833667-6f96ac9f4b18?auto=format&fit=crop&w=800&q=80",
            "category": "Classic"
        },
        {
            "title": "Sansevieria 'Cleopatra'",
            "description": "Intricate cross-banding and highly rigid, cascading form. Grows slowly but blooms magnificently.",
            "size": "Small",
            "light_level": "Medium Indirect",
            "price": 60.00,
            "image_url": "images/cleopatra.png", # Fully resolved with custom AI mapping
            "category": "Premium"
        },
        {
            "title": "Sansevieria 'Fernwood'",
            "description": "Dark green cylindrical leaves punctuated by light green tiger stripes. Exceptionally hardy.",
            "size": "Medium",
            "light_level": "Low to Bright Indirect",
            "price": 32.00,
            "image_url": "https://images.unsplash.com/photo-1687552212914-03a30c82053c?auto=format&fit=crop&w=800&q=80",
            "category": "Modern"
        },
        {
            "title": "Sansevieria 'Mikado'",
            "description": "A dense hybrid creating a beautiful thicket of spiky, fountain-like cylindrical fronds.",
            "size": "Medium",
            "light_level": "Medium Indirect",
            "price": 29.00,
            "image_url": "https://images.unsplash.com/photo-1695742339593-9d0488a7dfe7?auto=format&fit=crop&w=800&q=80",
            "category": "Modern"
        }
    ]

    for p_data in products_to_seed:
        product = db.query(Product).filter(Product.title == p_data["title"]).first()
        if not product:
            new_product = Product(**p_data)
            db.add(new_product)
            logger.info(f"Seeded product: {p_data['title']}")
        else:
            logger.info(f"Product {p_data['title']} already exists. Updating properties.")
            for key, value in p_data.items():
                setattr(product, key, value)

    db.commit()
    generate_mock_historical_orders(db)


def _seed_mock_users(db: Session, count: int) -> list[User]:
    users: list[User] = []
    for i in range(1, count + 1):
        email = f"mock.user{i:02d}@example.com"
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                name=f"Mock User {i:02d}",
                email=email,
                password_hash=get_password_hash("password123")
            )
            db.add(user)
            db.flush()
        users.append(user)
    db.commit()
    return users


def _weighted_sample_unique(products: list[Product], weights: list[float], count: int) -> list[Product]:
    pool_products = products[:]
    pool_weights = weights[:]
    selected: list[Product] = []
    for _ in range(min(count, len(pool_products))):
        chosen = random.choices(pool_products, weights=pool_weights, k=1)[0]
        idx = pool_products.index(chosen)
        selected.append(chosen)
        pool_products.pop(idx)
        pool_weights.pop(idx)
    return selected


def generate_mock_historical_orders(db: Session):
    random.seed(RANDOM_SEED)

    existing_mock_orders = db.query(Order).filter(Order.order_id.like(f"{MOCK_ORDER_PREFIX}%")).count()
    if existing_mock_orders > 0:
        logger.info(
            f"Historical mock data already exists ({existing_mock_orders} orders with prefix {MOCK_ORDER_PREFIX}). Skipping generation."
        )
        return

    products = db.query(Product).all()
    if not products:
        logger.warning("Cannot seed historical orders: no products found.")
        return

    users = _seed_mock_users(db, HISTORICAL_USER_COUNT)
    all_users = db.query(User).all()
    if not all_users:
        logger.warning("Cannot seed historical orders: no users found.")
        return

    # Skew product demand to make top/bottom sellers visible in analytics.
    popularity_weights = []
    for idx, _ in enumerate(products):
        if idx == 0:
            popularity_weights.append(10.0)
        elif idx in (1, 2, 3):
            popularity_weights.append(7.0)
        elif idx in (4, 5, 6):
            popularity_weights.append(5.0)
        else:
            popularity_weights.append(2.0)

    now_utc = datetime.now(timezone.utc)
    status_choices = ["COMPLETED", "PENDING", "FAILED"]
    status_weights = [0.84, 0.10, 0.06]

    created_orders = 0
    for i in range(1, HISTORICAL_ORDER_COUNT + 1):
        user = random.choice(all_users)

        days_ago = random.randint(0, HISTORICAL_DAYS - 1)
        seconds_in_day = random.randint(0, 86399)
        created_at = now_utc - timedelta(days=days_ago, seconds=seconds_in_day)

        status = random.choices(status_choices, weights=status_weights, k=1)[0]
        line_count = random.choices([1, 2, 3, 4], weights=[0.45, 0.30, 0.18, 0.07], k=1)[0]

        chosen_products = _weighted_sample_unique(products, popularity_weights, line_count)
        order_items: list[OrderItem] = []
        total_amount = 0.0

        for product in chosen_products:
            quantity = random.choices([1, 2, 3, 4], weights=[0.58, 0.27, 0.11, 0.04], k=1)[0]
            price_variation = random.uniform(0.92, 1.08)
            unit_price = round(float(product.price) * price_variation, 2)
            line_total = round(unit_price * quantity, 2)
            total_amount += line_total
            order_items.append(
                OrderItem(
                    product_id=product.id,
                    quantity=quantity,
                    price_at_purchase=unit_price
                )
            )

        order_id = f"{MOCK_ORDER_PREFIX}{created_at.strftime('%Y%m%d')}-{i:05d}"
        order = Order(
            order_id=order_id,
            user_id=user.id,
            status=status,
            total_amount=round(total_amount, 2),
            created_at=created_at
        )
        if status in ("COMPLETED", "FAILED"):
            order.updated_at = created_at + timedelta(hours=random.randint(1, 72))
        else:
            order.updated_at = created_at + timedelta(hours=random.randint(0, 12))

        db.add(order)
        db.flush()

        for item in order_items:
            item.order_id = order.id
            db.add(item)

        created_orders += 1
        if i % 50 == 0:
            db.commit()

    db.commit()
    logger.info(
        f"Seeded historical mock data: users={len(users)} orders={created_orders} days={HISTORICAL_DAYS}"
    )

def run_seed():
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting seed script...")
    run_seed()
    logger.info("Seed script finished successfully.")
