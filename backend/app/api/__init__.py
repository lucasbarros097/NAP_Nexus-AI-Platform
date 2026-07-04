"""API routes module."""

from fastapi import APIRouter

router = APIRouter()

from app.api import agents, projects, health

router.include_router(health.router, prefix="")
router.include_router(agents.router)
router.include_router(projects.router)
