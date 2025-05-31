from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
# from fastapi_mcp import FastApiMCP  # Install with: pip install fastapi-mcp
import time
import logging
from app.core.config import settings
from app.api.v1.endpoints import auth
from app.api.v1.endpoints.user import profile
from app.api.v1.endpoints.lov import answer_type
from app.db.session import get_db_pool
from app.core.cache import redis
from app.core.errors import error_handler
from app.core.rate_limit import rate_limit_middleware
from fastapi_mcp import FastApiMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up application...")
    app.state.db_pool = await get_db_pool()
    # Test Redis connection and clear cache
    try:
        await redis.ping()
        await redis.flushall()  # Clear all cache on startup
        logger.info("Redis connection successful and cache cleared")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
    yield
    # Shutdown
    logger.info("Shutting down application...")
    app.state.db_pool.close()
    await app.state.db_pool.wait_closed()
    await redis.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Configure CORS first (before other middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware (exclude MCP endpoints)
@app.middleware("http")
async def conditional_rate_limit(request: Request, call_next):
    if request.url.path.startswith("/mcp"):
        return await call_next(request)
    return await rate_limit_middleware(request, call_next)

# Add error handler last
app.add_exception_handler(Exception, error_handler)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} completed in {process_time:.3f}s")
    return response

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/favicon.ico")
async def get_favicon():
    return FileResponse("static/favicon.ico")

@app.get("/")
async def root():
    return {"message": "Hello World"}

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(profile.router, prefix=f"{settings.API_V1_STR}/profile", tags=["profile"])
app.include_router(answer_type.router, prefix=f"{settings.API_V1_STR}/answer-type", tags=["answer-type"])

# Setup MCP server after all endpoints are defined
# Use a shorter name to avoid tool naming issues
mcp = FastApiMCP(app, name="api")
mcp.mount()