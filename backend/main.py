import uvicorn

from app.core.config import settings
from app.main import app  # noqa: F401

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)