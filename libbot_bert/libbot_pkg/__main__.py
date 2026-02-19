import uvicorn
from .config import settings

uvicorn.run(
    "libbot_pkg.api:app",
    host=settings.host,
    port=settings.port,
    reload=False,  # set to True during development for auto-reloading on file changes
)