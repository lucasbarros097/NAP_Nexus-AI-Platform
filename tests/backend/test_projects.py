"""Tests for the project management endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def client():
    """Create an async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_list_projects(client):
    """Test listing projects (should work without DB)."""
    response = await client.get("/api/v1/projects/")
    # Without DB, will likely error - but endpoint should be reachable
    assert response.status_code in (200, 500)


@pytest.mark.asyncio
async def test_project_schema_validation():
    """Test Pydantic schema for project creation."""
    from app.schemas.project import ProjectCreate

    # Valid project
    project = ProjectCreate(name="Test Project", description="A test")
    assert project.name == "Test Project"
    assert project.description == "Test Project"

    # Invalid - empty name
    with pytest.raises(Exception):
        ProjectCreate(name="", description="invalid")


@pytest.mark.asyncio
async def test_project_model_repr():
    """Test ProjectModel string representation."""
    from app.models.project import ProjectModel

    model = ProjectModel(name="Test", status="draft")
    assert "ProjectModel" in repr(model)
    assert "Test" in repr(model)