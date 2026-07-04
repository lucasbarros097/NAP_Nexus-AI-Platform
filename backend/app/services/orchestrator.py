"""Orchestrator agent - coordinates task decomposition and agent execution."""

import json
import logging
from typing import Any

from app.services.openrouter import openrouter_service

logger = logging.getLogger(__name__)

# System prompt for the Orchestrator agent
ORCHESTRATOR_SYSTEM_PROMPT = """Você é o Orchestrator da NAP (Nexus AI Platform),
um arquiteto de software especialista em decompor problemas complexos em tarefas 
menores que serão executadas por agentes especializados.

Agentes disponíveis:
- backend: Gera código Python (FastAPI, SQLAlchemy, Pydantic)
- frontend: Gera componentes React/Next.js (TypeScript, TailwindCSS)
- documentation: Gera documentação técnica e ADRs
- reviewer: Valida código gerado (sintaxe, boas práticas, segurança)

Para cada requisição do usuário, você deve:
1. Analisar o requisito completo
2. Decompor em tarefas atômicas
3. Atribuir cada tarefa ao agente apropriado
4. Definir dependências entre as tarefas
5. Definir o formato de saída esperado para cada tarefa"""


class OrchestratorAgent:
    """Coordinates the multi-agent workflow for software generation."""

    def __init__(self):
        self.openrouter = openrouter_service

    async def decompose_task(self, user_request: str) -> list[dict[str, Any]]:
        """Break down a user request into sub-tasks for specialized agents.

        Args:
            user_request: The user's software requirements description.

        Returns:
            List of task dictionaries with agent_type, description, dependencies.
        """
        output_schema = {
            "type": "object",
            "properties": {
                "tasks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "agent_type": {
                                "type": "string",
                                "enum": [
                                    "backend",
                                    "frontend",
                                    "documentation",
                                    "reviewer",
                                ],
                            },
                            "description": {"type": "string"},
                            "dependencies": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "output_format": {"type": "string"},
                            "priority": {"type": "integer"},
                        },
                        "required": [
                            "id",
                            "agent_type",
                            "description",
                            "dependencies",
                            "priority",
                        ],
                    },
                },
                "analysis": {
                    "type": "object",
                    "properties": {
                        "project_type": {"type": "string"},
                        "complexity": {"type": "string"},
                        "estimated_agents_needed": {"type": "integer"},
                    },
                    "required": [
                        "project_type",
                        "complexity",
                        "estimated_agents_needed",
                    ],
                },
            },
            "required": ["tasks", "analysis"],
        }

        try:
            result = await self.openrouter.structured_completion(
                system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
                user_prompt=(
                    f"Analise e decomponha o seguinte requisito de software "
                    f"em tarefas para os agentes da NAP:\n\n{user_request}"
                ),
                output_schema=output_schema,
            )
            return result.get("tasks", [])
        except (RuntimeError, ValueError) as e:
            logger.error("Task decomposition failed: %s", e)
            # Fallback: return a single backend task
            return [
                {
                    "id": "task-1",
                    "agent_type": "backend",
                    "description": user_request,
                    "dependencies": [],
                    "priority": 1,
                }
            ]

    async def execute_workflow(self, user_request: str) -> dict[str, Any]:
        """Execute the full workflow: decompose -> assign -> collect results.

        Args:
            user_request: The user's software requirements description.

        Returns:
            Consolidated results from all agents.
        """
        logger.info("Starting workflow for request: %s", user_request[:100])

        # Step 1: Decompose the task
        tasks = await self.decompose_task(user_request)
        logger.info("Decomposed into %d tasks", len(tasks))

        # Step 2: Execute tasks in order (simplified sequential execution)
        results = {}
        for task in sorted(tasks, key=lambda t: t.get("priority", 99)):
            agent_type = task["agent_type"]
            description = task["description"]

            logger.info(
                "Executing task %s with agent %s: %s",
                task["id"], agent_type, description[:80]
            )

            # Route to appropriate agent
            agent_result = await self._route_to_agent(agent_type, description)
            results[task["id"]] = {
                "agent_type": agent_type,
                "task_id": task["id"],
                "status": "completed",
                "result": agent_result,
            }

        return {
            "status": "completed",
            "total_tasks": len(tasks),
            "results": results,
        }

    async def _route_to_agent(
        self, agent_type: str, task: str
    ) -> dict[str, Any]:
        """Route a task to the appropriate agent for execution.

        Args:
            agent_type: The type of agent (backend, frontend, etc.)
            task: The task description.

        Returns:
            Agent execution result with generated code/docs and metadata.
        """
        agent_prompts = {
            "backend": {
                "system": (
                    "Você é um especialista em desenvolvimento backend Python. "
                    "Gere código limpo e bem estruturado usando FastAPI, "
                    "SQLAlchemy e Pydantic. Inclua type hints e docstrings."
                ),
                "output_key": "generated_code",
            },
            "frontend": {
                "system": (
                    "Você é um especialista em frontend React/Next.js. "
                    "Gere componentes com TypeScript, TailwindCSS e boas "
                    "práticas de acessibilidade e performance."
                ),
                "output_key": "generated_code",
            },
            "documentation": {
                "system": (
                    "Você é um documentador técnico especializado. "
                    "Gere documentação clara, incluindo ADRs, READMEs "
                    "e docstrings para o código gerado."
                ),
                "output_key": "documentation",
            },
            "reviewer": {
                "system": (
                    "Você é um revisor de código experiente. "
                    "Analise o código gerado em busca de bugs, más práticas, "
                    "vulnerabilidades e sugira melhorias específicas."
                ),
                "output_key": "review_report",
            },
        }

        agent_config = agent_prompts.get(agent_type, agent_prompts["backend"])
        output_key = agent_config["output_key"]

        try:
            content = await self.openrouter.chat_completion(
                system_prompt=agent_config["system"],
                user_prompt=(
                    f"Execute a seguinte tarefa:\n\n{task}\n\n"
                    f"Gere o resultado completo e detalhado."
                ),
            )
            return {output_key: content, "length": len(content)}
        except RuntimeError as e:
            logger.error("Agent %s failed: %s", agent_type, e)
            return {output_key: f"Error: {str(e)}", "error": True}


# Singleton instance
orchestrator = OrchestratorAgent()