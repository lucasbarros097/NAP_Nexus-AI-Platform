"""Pydantic schemas for Project."""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Any


class ProjectCreate(BaseModel):
    """Schema for creating a new project."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    metadata_json: dict[str, Any] = {}


class ProjectUpdate(BaseModel):
    """Schema for updating an existing project."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    metadata_json: Optional[dict[str, Any]] = None


class ProjectRead(BaseModel):
    """Schema for reading/returning a project."""
    id: int
    name: str
    description: Optional[str] = None
    status: str
    metadata_json: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}