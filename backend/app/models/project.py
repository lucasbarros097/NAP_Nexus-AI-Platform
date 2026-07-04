"""Project SQLAlchemy model."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional, List

from app.core.database import Base


class ProjectModel(Base):
    """Represents a software project managed by NAP."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="draft")  # draft, active, completed, archived
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    async def get_all(cls, db: AsyncSession) -> List["ProjectModel"]:
        result = await db.execute(select(cls).order_by(cls.created_at.desc()))
        return result.scalars().all()

    @classmethod
    async def get_by_id(cls, db: AsyncSession, project_id: int) -> Optional["ProjectModel"]:
        result = await db.execute(select(cls).where(cls.id == project_id))
        return result.scalar_one_or_none()

    @classmethod
    async def create(cls, db: AsyncSession, **kwargs) -> "ProjectModel":
        instance = cls(**kwargs)
        db.add(instance)
        await db.flush()
        await db.refresh(instance)
        return instance

    def __repr__(self) -> str:
        return f"<ProjectModel(id={self.id}, name='{self.name}', status='{self.status}')>"