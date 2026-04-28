"""
Marketplace Cafetero – Backend API
Punto de entrada principal de la aplicación FastAPI.

Arquitectura en capas (RNF-007.1):
  routes/       → Controladores / handlers HTTP
  services/     → Lógica de negocio
  repositories/ → Acceso a Firestore / Firebase Storage
  models/       → Esquemas Pydantic y modelos de datos
"""

import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Cargar variables de entorno desde .env
load_dotenv()

logger = logging.getLogger(__name__)

# Inicializar Firebase Admin SDK al importar el módulo (antes de cualquier router)
def _init_firebase() -> None:
    """Inicializar Firebase Admin SDK con las credenciales del entorno."""
    import firebase_admin
    from firebase_admin import credentials

    if firebase_admin._apps:
        return

    credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase-service-account.json")
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    storage_bucket = os.getenv("FIREBASE_STORAGE_BUCKET")

    if os.path.exists(credentials_path):
        cred = credentials.Certificate(credentials_path)
        firebase_admin.initialize_app(
            cred,
            {
                "projectId": project_id,
                "storageBucket": storage_bucket,
            },
        )
        print(f"[INFO] Firebase initialized with project '{project_id}'")
    else:
        print(
            f"[WARNING] Firebase credentials file not found at '{credentials_path}'. "
            "Firebase features will not work until credentials are configured."
        )

_init_firebase()

# Importar routers (se registrarán a medida que se implementen las tareas)
from routes.auth import router as auth_router
from routes.products import router as products_router
from routes.producers import router as producers_router
from routes.cart import router as cart_router
from routes.orders import router as orders_router
from routes.payments import router as payments_router
from routes.shipping import router as shipping_router
from routes.sales import router as sales_router
from routes.addresses import router as addresses_router
from routes.admin import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación."""
    # Firebase ya fue inicializado al importar el módulo
    yield
    # Shutdown: liberar recursos si es necesario


def _init_firebase() -> None:
    """Inicializar Firebase Admin SDK con las credenciales del entorno."""
    import firebase_admin
    from firebase_admin import credentials

    if firebase_admin._apps:
        # Ya inicializado (evitar doble inicialización en tests)
        return

    credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase-service-account.json")
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    storage_bucket = os.getenv("FIREBASE_STORAGE_BUCKET")

    if os.path.exists(credentials_path):
        cred = credentials.Certificate(credentials_path)
        firebase_admin.initialize_app(
            cred,
            {
                "projectId": project_id,
                "storageBucket": storage_bucket,
            },
        )
    else:
        # En entorno de desarrollo sin credenciales reales, usar credenciales de aplicación por defecto
        # o simplemente registrar una advertencia
        print(
            f"[WARNING] Firebase credentials file not found at '{credentials_path}'. "
            "Firebase features will not work until credentials are configured."
        )


# Crear instancia de la aplicación FastAPI
app = FastAPI(
    title="The Artisanal Connection API",
    description=(
        "API REST para The Artisanal Connection – conecta productores de café colombiano "
        "con consumidores finales.\n\n"
        "## Autenticación\n"
        "La mayoría de endpoints requieren un Firebase ID Token en el header:\n"
        "`Authorization: Bearer <firebase_id_token>`\n\n"
        "## Roles\n"
        "- **CONSUMER**: consumidor final que navega el catálogo y realiza pedidos.\n"
        "- **PRODUCER**: productor de café que gestiona productos y ventas.\n"
        "- **ADMIN**: administrador de la plataforma.\n\n"
        "## Formato de errores\n"
        "Todos los errores siguen el formato uniforme:\n"
        "```json\n"
        '{"error": {"code": "VALIDATION_ERROR", "message": "...", "fields": [...]}}\n'
        "```\n\n"
        "## Especificación OpenAPI\n"
        "La especificación completa está disponible en `openapi.yaml` en la raíz del backend. "
        "(RNF-007.2)"
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    contact={"name": "The Artisanal Connection"},
    license_info={"name": "Privado"},
)

# Configurar CORS (RNF-003.1 – solo HTTPS en producción)
cors_origins_raw = os.getenv("CORS_ORIGINS", "http://localhost:5173")
cors_origins = [origin.strip() for origin in cors_origins_raw.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"https://.*\.ngrok-free\.app|https://.*\.ngrok\.io|https://.*\.ngrok-free\.dev",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Middleware para bypass de la página de advertencia de ngrok
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest

class NgrokBypassMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        response = await call_next(request)
        response.headers["ngrok-skip-browser-warning"] = "true"
        return response

app.add_middleware(NgrokBypassMiddleware)

# Registrar routers
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(products_router, prefix="/api/products", tags=["products"])
app.include_router(producers_router, prefix="/api/producers", tags=["producers"])
app.include_router(cart_router, prefix="/api/cart", tags=["cart"])
app.include_router(orders_router, prefix="/api/orders", tags=["orders"])
app.include_router(payments_router, prefix="/api/payments", tags=["payments"])
app.include_router(shipping_router, prefix="/api/shipping", tags=["shipping"])
app.include_router(sales_router, prefix="/api/sales", tags=["sales"])
app.include_router(addresses_router, prefix="/api/addresses", tags=["addresses"])
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handler global para excepciones no manejadas.
    Garantiza que los headers CORS estén presentes incluso en errores 500,
    evitando que el browser reporte un error de CORS en lugar del error real.
    """
    origin = request.headers.get("origin", "")
    headers = {}
    if origin:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"

    logger.error("Unhandled exception on %s %s: %s", request.method, request.url.path, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "Error interno del servidor."}},
        headers=headers,
    )


@app.get("/", tags=["health"])
async def root():
    """Health check – verifica que el servidor está activo."""
    return {"status": "ok", "service": "The Artisanal Connection API", "version": "0.1.0"}


@app.get("/health", tags=["health"])
async def health_check():
    """Health check detallado."""
    return {
        "status": "ok",
        "environment": os.getenv("APP_ENV", "development"),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", "8000")),
        reload=os.getenv("APP_DEBUG", "true").lower() == "true",
    )
