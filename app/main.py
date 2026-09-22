from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.auth import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.api.submissions import router as submissions_router
from app.api.widgets import router as widgets_router
from app.core.config import settings


MAX_REQUEST_SIZE = 64 * 1024

limiter = Limiter(
    key_func=get_remote_address,
)


app = FastAPI(
    title="FlyRank Capstone Widget Platform",
    version="1.0.0",
    description="Embeddable widget and lead-capture platform for the FlyRank capstone.",
)


# -------------------------------------------------------------------
# Rate limiting
# -------------------------------------------------------------------

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)


# -------------------------------------------------------------------
# CORS
# -------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in settings.cors_origins.split(",")
        if origin.strip()
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------------
# Request size protection
# -------------------------------------------------------------------

@app.middleware("http")
async def request_size_limit(request: Request, call_next):
    content_length = request.headers.get("content-length")

    if content_length:
        try:
            if int(content_length) > MAX_REQUEST_SIZE:
                return JSONResponse(
                    status_code=413,
                    content={
                        "detail": "Request body is too large"
                    },
                )

        except ValueError:
            return JSONResponse(
                status_code=400,
                content={
                    "detail": "Invalid Content-Length header"
                },
            )

    return await call_next(request)


# -------------------------------------------------------------------
# Health check
# -------------------------------------------------------------------

@app.get(
    "/health",
    tags=["Health"],
)
def health_check():
    return {
        "status": "ok",
        "service": "flyrank-capstone-api",
    }


# -------------------------------------------------------------------
# API routers
# -------------------------------------------------------------------

app.include_router(auth_router)

app.include_router(widgets_router)

app.include_router(submissions_router)

app.include_router(dashboard_router)