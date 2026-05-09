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
    """Swap all agents to a local Ollama model via LiteLlm for offline testing.

    Default: qwen3:8b — solid tool-calling on a 16GB Mac.
    Alternatives (pull with `ollama pull <name>`):
      - qwen2.5:7b                  : a touch smaller/faster, slightly weaker at tools
      - qwen2.5:14b-instruct-q4_K_M : noticeably better reasoning, ~9GB RAM, slower
      - qwen2.5:3b                  : minimum viable, struggles past ~4 tools
    """
    from google.adk.models.lite_llm import LiteLlm
    from shopaiholic.agents import root_agent
    from shopaiholic.agents.meal_planner import meal_planner
    from shopaiholic.agents.ingredient_aggregator import ingredient_aggregator
    from shopaiholic.agents.store_finder import store_finder
    from shopaiholic.agents.store_buyer import store_buyer

    model = LiteLlm(model="ollama/qwen3:8b")

    for agent in [root_agent, meal_planner, ingredient_aggregator, store_finder, store_buyer]:
        agent.model = model


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
