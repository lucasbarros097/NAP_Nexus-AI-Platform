"""Tests for the health check endpoints."""

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
async def test_health_endpoint(client):
    """Test the root health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "NAP - Nexus AI Platform"
    assert "version" in data


@pytest.mark.asyncio
async def test_system_info(client):
    """Test the system info endpoint."""
    response = await client.get("/api/v1/system")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "version" in data
    assert "model" in data


@pytest.mark.asyncio
async def test_openrouter_service_initialization():
    """Test that OpenRouter service initializes without API key."""
    from app.services.openrouter import OpenRouterService
    service = OpenRouterService()
    assert service.model == "deepseek/deepseek-chat:free"
    assert service.base_url == "https://openrouter.ai/api/v1"


@pytest.mark.asyncio
async def test_orchestrator_initialization():
    """Test that Orchestrator initializes correctly."""
    from app.services.orchestrator import OrchestratorAgent
    orchestrator = OrchestratorAgent()
    assert orchestrator is not None