from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    size = Column(String)
    light_level = Column(String)
    price = Column(Float)
    image_url = Column(String)
    category = Column(String)
