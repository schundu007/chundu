from .jobs import router as jobs_router
from .applications import router as applications_router
from .documents import router as documents_router
from .settings import router as settings_router

__all__ = [
    "jobs_router",
    "applications_router",
    "documents_router",
    "settings_router",
]
