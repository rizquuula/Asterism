"""API routes module."""

from .chat import router as chat_router
from .config import router as config_router
from .health import router as health_router
from .models import router as models_router

__all__ = ["chat_router", "config_router", "health_router", "models_router"]
