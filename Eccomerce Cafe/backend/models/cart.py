from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
try:
    from database import Base
except ImportError:
    from backend.database import Base

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    variant_id = Column(Integer, ForeignKey("product_variants.id"))
    quantity = Column(Integer, default=1)

    variant = relationship("ProductVariant")
