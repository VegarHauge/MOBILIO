from sqlalchemy import Column, Integer, String, Float, Text, DECIMAL
from db.base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text)
    brand = Column(String(255))
    rating = Column(DECIMAL)
    ratings = Column(Integer)
    stock = Column(Integer)
    category = Column(String(255))
    picture = Column(String(255))