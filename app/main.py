import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.routers.products import router as products_router
from app.seed import seed_database
from app.models import ErrorResponse, ErrorDetail
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Product Management API", version="1.0.0")

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# ✅ MUST BE FIRST
@app.get("/__/auth/{path:path}")
async def firebase_auth_handler():
    return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head><title>Auth</title></head>
        <body>
        <script>
            // Let Firebase complete the login flow
            window.opener && window.opener.postMessage(location.href, "*");
            window.close();
        </script>
        </body>
        </html>
    """)
# Mount static files
app.mount("/static", StaticFiles(directory="app/static",html=True), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(products_router, prefix="/api/v1/products", tags=["products"])

@app.on_event("startup")
async def startup_event():
    await seed_database()

# Global exception handlers for consistent error responses
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    error_response = ErrorResponse(
        error="http_error",
        message=exc.detail,
        code=f"HTTP_{exc.status_code}",
        timestamp=datetime.utcnow().isoformat()
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append(ErrorDetail(
            field=".".join(str(loc) for loc in error["loc"]),
            message=error["msg"],
            code=error["type"]
        ))
    
    error_response = ErrorResponse(
        error="validation_error",
        message="Request validation failed",
        code="VALIDATION_ERROR",
        details=errors,
        timestamp=datetime.utcnow().isoformat()
    )
    return JSONResponse(
        status_code=422,
        content=error_response.dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    error_response = ErrorResponse(
        error="internal_server_error",
        message="An unexpected error occurred",
        code="INTERNAL_ERROR",
        timestamp=datetime.utcnow().isoformat()
    )
    return JSONResponse(
        status_code=500,
        content=error_response.dict()
    )

# GUI routes
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/create")
async def create_page(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})

@app.get("/update/{product_id}")
async def update_page(request: Request, product_id: str):
    return templates.TemplateResponse("update.html", {"request": request, "product_id": product_id})

@app.get("/search")
async def search_page(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})


@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})