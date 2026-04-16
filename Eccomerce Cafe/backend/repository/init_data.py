from sqlalchemy.orm import Session
try:
    from models.user import User
    from models.product import Product, ProductVariant
    from repository.user_repository import create_user
    from schemas.user import UserCreate
except ImportError:
    from backend.models.user import User
    from backend.models.product import Product, ProductVariant
    from backend.repository.user_repository import create_user
    from backend.schemas.user import UserCreate

def seed_test_data(db: Session):
    # Check if we already have test producers
    producer = db.query(User).filter(User.email == "producer@example.com").first()
    if not producer:
        producer = create_user(db, UserCreate(email="producer@example.com", password="producerpassword123", role="Productor"))
        
        product1 = Product(name="Café Genuino", producer_id=producer.id, description="Café artesanal colombiano")
        db.add(product1)
        db.commit()
        db.refresh(product1)

        v1 = ProductVariant(product_id=product1.id, name="250g Grano", price=12.0, stock=50, iva_percentage=19.0)
        v2 = ProductVariant(product_id=product1.id, name="500g Molienda Fina", price=22.0, stock=30, iva_percentage=19.0)
        
        db.add_all([v1, v2])
        db.commit()

        product2 = Product(name="Café Gourmet Excelso", producer_id=producer.id, description="Selección especial")
        db.add(product2)
        db.commit()
        db.refresh(product2)

        v3 = ProductVariant(product_id=product2.id, name="1kg Grano Entero", price=40.0, stock=10, iva_percentage=19.0)
        db.add(v3)
        db.commit()

        # Producer 2
        producer2 = create_user(db, UserCreate(email="producer2@example.com", password="prod2password", role="Productor"))
        
        product3 = Product(name="Café Descafeinado Suave", producer_id=producer2.id, description="Descafeinado natural")
        db.add(product3)
        db.commit()
        db.refresh(product3)

        v4 = ProductVariant(product_id=product3.id, name="500g Molienda Media", price=25.0, stock=20, iva_percentage=19.0)
        db.add(v4)
        db.commit()
