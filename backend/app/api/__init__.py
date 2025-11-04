from fastapi import APIRouter
from .characters import router as characters_router
from .projects import router as projects_router
from .generation import router as generation_router

api_router = APIRouter()

api_router.include_router(
    characters_router,
    prefix="/characters",
    tags=["characters"]
)

api_router.include_router(
    projects_router,
    prefix="/projects",
    tags=["projects"]
)

api_router.include_router(
    generation_router,
    prefix="/generation",
    tags=["generation"]
)
