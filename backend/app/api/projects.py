"""Project management endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_session
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.models.project import ProjectModel

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=List[ProjectRead])
async def list_projects(db: AsyncSession = Depends(get_session)):
    """List all projects."""
    return await ProjectModel.get_all(db)


@router.post("/", response_model=ProjectRead, status_code=201)
async def create_project(project: ProjectCreate, db: AsyncSession = Depends(get_session)):
    """Create a new project."""
    return await ProjectModel.create(db, **project.model_dump())


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(project_id: int, db: AsyncSession = Depends(get_session)):
    """Get a project by ID."""
    project = await ProjectModel.get_by_id(db, project_id)
    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")
    return project