"""Agent management and execution endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any

from app.services.orchestrator import orchestrator

router = APIRouter(prefix="/agents", tags=["agents"])


class AgentRequest(BaseModel):
    """Request to execute a task with an agent."""
    agent_type: str  # "architect", "backend", "frontend", "documentation", "reviewer"
    task: str
    context: dict = {}


class AgentResponse(BaseModel):
    """Response from an agent execution."""
    agent_type: str
    status: str
    result: dict[str, Any]
    artifacts: list[str] = []


class WorkflowRequest(BaseModel):
    """Request to execute a full multi-agent workflow."""
    task: str
    context: dict = {}


class WorkflowResponse(BaseModel):
    """Response from a full workflow execution."""
    status: str
    total_tasks: int
    results: dict[str, Any]


@router.post("/execute", response_model=AgentResponse)
async def execute_agent(request: AgentRequest):
    """Execute a task with the specified agent type."""
    agent_types = {"architect", "backend", "frontend", "documentation", "reviewer"}
    if request.agent_type not in agent_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid agent type. Must be one of: {agent_types}",
        )

    # Route to the orchestrator's agent execution
    result = await orchestrator._route_to_agent(
        request.agent_type, request.task
    )

    return AgentResponse(
        agent_type=request.agent_type,
        status="completed" if not result.get("error") else "failed",
        result=result,
        artifacts=[],
    )


@router.post("/workflow", response_model=WorkflowResponse)
async def execute_workflow(request: WorkflowRequest):
    """Execute a full multi-agent workflow from a user request."""
    result = await orchestrator.execute_workflow(request.task)
    return WorkflowResponse(
        status=result["status"],
        total_tasks=result["total_tasks"],
        results=result["results"],
    )
