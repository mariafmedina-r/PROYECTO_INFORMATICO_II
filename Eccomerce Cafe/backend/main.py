from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

try:
    from database import engine, Base, SessionLocal
    from routers import user_router, product_router, cart_router, order_router
    from repository.user_repository import init_test_user
    from repository.init_data import seed_test_data
    import models.product
    import models.cart
    import models.order
except ImportError:
    from backend.database import engine, Base, SessionLocal
    from backend.routers import user_router, product_router, cart_router, order_router
    from backend.repository.user_repository import init_test_user
    from backend.repository.init_data import seed_test_data
    import backend.models.product
    import backend.models.cart
    import backend.models.order

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the database tables if they do not exist
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created successfully.")
except Exception as e:
    logger.error(f"Failed to create database tables: {e}")

# Initialize test user and test products data
try:
    db = SessionLocal()
    init_test_user(db)
    seed_test_data(db)
    db.close()
    logger.info("Test user and product seed data verified/created successfully.")
except Exception as e:
    logger.error(f"Error initializing test data: {e}")

app = FastAPI(title="Coffee Commerce API", version="1.0.0")

# CORS setup as suggested in guia.txt
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler to absolutely prevent crashes
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception occurred: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": f"An unexpected error occurred: {str(exc)}",
            "path": request.url.path
        }
    )

app.include_router(user_router.router)
app.include_router(product_router.router)
app.include_router(cart_router.router)
app.include_router(order_router.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Coffee Commerce API. The application is running successfully."}
