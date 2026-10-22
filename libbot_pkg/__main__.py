import uvicorn
from .config import load_settings
from .api import create_app

settings = load_settings()
my_app = create_app(settings)

# Unvicorn is an ASGI server that can run FastAPI applications.
# Here we specify the app location and server settings.
uvicorn.run(
    #"libbot_pkg.api:app",
    my_app,
    host=settings.host,
    port=settings.port,
    reload=False,  # set to True during development for auto-reloading on file changes
)