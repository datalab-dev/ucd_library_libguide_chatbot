import uvicorn
from .config import settings

# Unvicorn is an ASGI server that can run FastAPI applications.
# Here we specify the app location and server settings.
uvicorn.run(
    "libbot_pkg.api:app",
    host=settings.host,
    port=settings.port,
    reload=False,  # set to True during development for auto-reloading on file changes
)