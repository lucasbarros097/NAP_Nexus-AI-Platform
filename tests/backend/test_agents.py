"""Tests for the agent execution endpoints."""

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
async def test_execute_agent_invalid_type(client):
    """Test agent execution with invalid agent type."""
    response = await client.post(
        "/api/v1/agents/execute",
        json={
            "agent_type": "invalid_type",
            "task": "do something",
        },
    )
    assert response.status_code == 400
    assert "Invalid agent type" in response.json()["detail"]


@pytest.mark.asyncio
async def test_execute_agent_valid_types(client):
    """Test that valid agent types are accepted."""
    agent_types = ["backend", "frontend", "documentation", "reviewer"]

    for agent_type in agent_types:
        response = await client.post(
            "/api/v1/agents/execute",
            json={
                "agent_type": agent_type,
                "task": "test task",
            },
        )
        # Without API key, should return error status
        assert response.status_code == 200
        data = response.json()
        assert data["agent_type"] == agent_type
        assert data["status"] in ("completed", "failed")


@pytest.mark.asyncio
async def test_execute_workflow_endpoint(client):
    """Test the workflow execution endpoint."""
    response = await client.post(
        "/api/v1/agents/workflow",
        json={
            "task": "Create a simple hello world API",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "total_tasks" in data
    assert "results" in data