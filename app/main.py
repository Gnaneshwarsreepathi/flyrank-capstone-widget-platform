from app.api.submissions import router as submissions_router
from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.widgets import router as widgets_router


app = FastAPI(
    title="FlyRank Capstone Widget Platform",
    version="1.0.0",
    description="Embeddable widget and lead-capture platform for the FlyRank capstone.",
)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "flyrank-capstone-api",
    }


app.include_router(auth_router)
app.include_router(widgets_router)
app.include_router(submissions_router)
