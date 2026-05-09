"""Runner and interactive chat entry point.

Usage:
    # Gemini (default, requires GOOGLE_API_KEY in .env)
    python -m shopaiholic.app

    # Local Qwen via Ollama (no API key needed)
    python -m shopaiholic.app --local
"""

from __future__ import annotations

import asyncio
import sys

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


APP_NAME = "shopaiholic"
USER_ID = "user_local"
SESSION_ID = "session_1"


def _build_runner(local: bool = False) -> Runner:
    from shopaiholic.config import require_google_api_key
    from shopaiholic.agents import root_agent
    from google.adk.plugins.reflect_retry_tool_plugin import ReflectAndRetryToolPlugin

    if local:
        _patch_agents_for_local()
    else:
        require_google_api_key()  # fail fast with a clear message

    return Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=InMemorySessionService(),
        plugins=[ReflectAndRetryToolPlugin()],
    )


def _patch_agents_for_local() -> None:
    """Swap all agents to qwen2.5:3b via LiteLlm for offline testing."""
    from google.adk.models.lite_llm import LiteLlm
    from shopaiholic.agents import root_agent

    qwen = LiteLlm(model="ollama/qwen2.5:3b")

    for agent in [root_agent] + list(root_agent.sub_agents):
        agent.model = qwen


async def run_chat(local: bool = False) -> None:
    runner = _build_runner(local=local)

    await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    print("ShopAIholic is ready. Type your message, or 'quit' to exit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        if not user_input:
            continue

        message = types.Content(
            role="user",
            parts=[types.Part(text=user_input)],
        )

        response_parts = []
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=message,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        response_parts.append(part.text)

        if response_parts:
            print(f"\nShopAIholic: {''.join(response_parts)}\n")


if __name__ == "__main__":
    local_mode = "--local" in sys.argv
    asyncio.run(run_chat(local=local_mode))
