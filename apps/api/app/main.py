"""FitSense API — FastAPI application entry point with hardened security and error handling."""

import logging
import time
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.limiter import limiter
from app.routers import (
    account,
    admin,
    ai,
    coverage,
    feedback,
    health,
    products,
    recommend,
    retailer,
    retailers,
)

# Configure structured privacy-safe logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("fitsense.api")

# Optional Sentry initialization
if settings.sentry_dsn:
    try:
        import sentry_sdk
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            traces_sample_rate=0.1,
            send_default_pii=False,  # Strictly NO personal data sent to Sentry
        )
        logger.info("Sentry error monitoring initialized.")
    except ImportError:
        logger.warning("sentry-sdk not installed; monitoring disabled.")

app = FastAPI(
    title="FitSense API",
    version=settings.app_version,
    description="Universal Fit Intelligence for Pakistani online fashion",
)

# Attach rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ---------------------------------------------------------------------------
# Consistent Error Format Handlers
# ---------------------------------------------------------------------------
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail if isinstance(exc.detail, str) else "Request error",
                "detail": exc.detail,
            },
            "detail": exc.detail,
        },
    )


@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed on request payload or parameters",
                "detail": exc.errors(),
            }
        },
    )


# ---------------------------------------------------------------------------
# Security Headers & Request Limits Middleware
# ---------------------------------------------------------------------------
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB limit for bulk CSV uploads; 2MB for standard requests


@app.middleware("http")
async def security_and_limits_middleware(request: Request, call_next):
    # Enforce request payload size limit
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_CONTENT_LENGTH:
        return JSONResponse(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            content={
                "error": {
                    "code": "PAYLOAD_TOO_LARGE",
                    "message": f"Request payload exceeds {MAX_CONTENT_LENGTH // (1024*1024)}MB maximum limit.",
                }
            },
        )

    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)

    # Privacy-preserving access log: never log body, auth headers, or measurements
    logger.info(f"{request.method} {request.url.path} -> HTTP {response.status_code} ({duration_ms}ms)")

    # Standard security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response


# ---------------------------------------------------------------------------
# Strict CORS Middleware
# ---------------------------------------------------------------------------
# Restrictive regex matching FitSense Vercel deployments (production and preview)
# Strictly anchored at both ends; does NOT allow arbitrary *.vercel.app sites
FITSENSE_VERCEL_ORIGIN_REGEX = (
    r"^https:\/\/universal-shopping-intelligence(-[a-zA-Z0-9_-]+)?\.vercel\.app$"
)

origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["http://localhost:3000"],
    allow_origin_regex=FITSENSE_VERCEL_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
)

# ---------------------------------------------------------------------------
# Register Routers
# ---------------------------------------------------------------------------
app.include_router(health.router)
app.include_router(ai.router)
app.include_router(products.router)
app.include_router(retailers.router)
app.include_router(coverage.router)
app.include_router(recommend.router)
app.include_router(feedback.router)
app.include_router(account.router)
app.include_router(retailer.router)
app.include_router(admin.router)
