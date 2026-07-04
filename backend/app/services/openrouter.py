"""OpenRouter API integration service for AI model access."""

import json
import logging
from typing import Optional

import httpx
from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenRouterService:
    """Service for interacting with OpenRouter API to access AI models."""

    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.model = settings.OPENROUTER_MODEL
        self.max_tokens = settings.OPENROUTER_MAX_TOKENS
        self.temperature = settings.OPENROUTER_TEMPERATURE

        if not self.api_key:
            logger.warning(
                "OPENROUTER_API_KEY not set. AI features will not work."
            )

        self.client = AsyncOpenAI(
            api_key=self.api_key or "sk-placeholder",
            base_url=self.base_url,
            http_client=httpx.AsyncClient(
                timeout=httpx.Timeout(120.0, connect=10.0),
                follow_redirects=True,
            ),
        )

    async def chat_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Send a chat completion request to OpenRouter.

        Args:
            system_prompt: System-level instruction for the model.
            user_prompt: The user's request/task description.
            temperature: Override default temperature.
            max_tokens: Override default max tokens.

        Returns:
            The model's response text.

        Raises:
            RuntimeError: If API key is not configured or request fails.
        """
        if not self.api_key:
            raise RuntimeError(
                "OpenRouter API key not configured. "
                "Set OPENROUTER_API_KEY in .env file."
            )

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                extra_headers={
                    "HTTP-Referer": "https://github.com/nap-nexus",
                    "X-Title": "NAP - Nexus AI Platform",
                },
            )

            content = response.choices[0].message.content
            if content is None:
                raise RuntimeError("Model returned empty response")

            logger.info(
                "OpenRouter response received: model=%s, tokens=%d",
                response.model,
                response.usage.total_tokens if response.usage else 0,
            )

            return content

        except Exception as e:
            logger.error("OpenRouter request failed: %s", str(e))
            raise RuntimeError(f"AI model request failed: {str(e)}") from e

    async def structured_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        output_schema: dict,
    ) -> dict:
        """Request a structured JSON response from the model.

        Args:
            system_prompt: System-level instruction.
            user_prompt: The user's request.
            output_schema: JSON schema description for the expected output.

        Returns:
            Parsed JSON response as a dictionary.
        """
        enhanced_system = (
            f"{system_prompt}\n\n"
            f"You MUST respond with valid JSON matching this schema:\n"
            f"{json.dumps(output_schema, indent=2)}\n\n"
            "Respond ONLY with the JSON object, no other text."
        )

        content = await self.chat_completion(
            system_prompt=enhanced_system,
            user_prompt=user_prompt,
            temperature=0.1,  # Low temperature for structured output
        )

        # Attempt to parse JSON from the response
        content_clean = content.strip()
        if content_clean.startswith("```json"):
            content_clean = content_clean[7:]
        if content_clean.startswith("```"):
            content_clean = content_clean[3:]
        if content_clean.endswith("```"):
            content_clean = content_clean[:-3]

        try:
            return json.loads(content_clean.strip())
        except json.JSONDecodeError as e:
            logger.error("Failed to parse JSON response: %s", e)
            logger.debug("Raw response: %s", content)
            raise ValueError(f"Invalid JSON response from model: {e}") from e


# Singleton instance
openrouter_service = OpenRouterService()