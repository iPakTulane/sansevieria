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
