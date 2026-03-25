import logging
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.models.product import Product
from app.utils.security import get_password_hash

logger = logging.getLogger(__name__)

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
    else:
        logger.info(f"User {test_email} already exists. Skipping.")

    # Seed Products
    products_to_seed = [
        {
            "title": "Sansevieria Trifasciata",
            "description": "The classic Snake Plant, known for its tall, upright leaves with yellow edges.",
            "size": "Medium",
            "light_level": "Low to Bright Indirect",
            "price": 25.00,
            "image_url": "/images/trifasciata.jpg",
            "category": "Classic"
        },
        {
            "title": "Sansevieria Cylindrica",
            "description": "Features round, cylindrical leaves that grow outward like a fan.",
            "size": "Small",
            "light_level": "Medium to Bright Indirect",
            "price": 30.00,
            "image_url": "/images/cylindrica.jpg",
            "category": "Rare"
        },
        {
            "title": "Sansevieria Moonshine",
            "description": "Broad, silvery-green leaves that bring a subtle brightness to any room.",
            "size": "Medium",
            "light_level": "Low to Bright Indirect",
            "price": 28.00,
            "image_url": "/images/moonshine.jpg",
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
            logger.info(f"Product {p_data['title']} already exists. Skipping.")

    db.commit()

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
