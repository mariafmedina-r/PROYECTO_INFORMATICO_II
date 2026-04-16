from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
try:
    from database import Base
except ImportError:
    from backend.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    producer_id = Column(Integer, ForeignKey("users.id"))
    description = Column(String, nullable=True)
    deleted_at = Column(DateTime, nullable=True) # Soft delete

    variants = relationship("ProductVariant", back_populates="product")
    producer = relationship("User")

class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    name = Column(String) # e.g. "500g Molienda Fina"
    price = Column(Float)
    stock = Column(Integer, default=0)
    iva_percentage = Column(Float, default=19.0) # Standard IVA

    product = relationship("Product", back_populates="variants")
