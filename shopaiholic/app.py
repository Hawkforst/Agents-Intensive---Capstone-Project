"""Runner and interactive chat entry point.

Usage:
    # Gemini (default, requires GOOGLE_API_KEY in .env)
    python -m shopaiholic.app

    # Groq (fast hosted, requires GROQ_API_KEY in .env)
    python -m shopaiholic.app --groq

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


def _build_runner(local: bool = False, groq: bool = False) -> Runner:
    from shopaiholic.config import require_google_api_key
    from shopaiholic.agents import root_agent

    if groq:
        _patch_agents_for_groq()
    elif local:
        _patch_agents_for_local()
    else:
        require_google_api_key()  # fail fast with a clear message

    # NOTE: ReflectAndRetryToolPlugin is intentionally disabled while the free
    # tier quota is tight — it amplifies 429 errors. Re-add for production:
    #   from google.adk.plugins.reflect_retry_tool_plugin import ReflectAndRetryToolPlugin
    #   plugins=[ReflectAndRetryToolPlugin()]
    return Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=InMemorySessionService(),
    )


def _patch_agents_for_local() -> None:
    """Swap all agents to a local Ollama model via LiteLlm for offline testing.

    Default: qwen3.5:4b — newer architecture, sweet spot for tool calling on a 16GB Mac.
    Alternatives (pull with `ollama pull <name>`):
      - qwen3.5:9b   : noticeably better reasoning, slower (~25 tok/s on M4)
      - qwen2.5:7b   : older but well-tested with LiteLLM, fallback if qwen3.5 has tool-call bugs
      - qwen3:8b     : avoid — thinking-mode breaks tool calling via LiteLLM
      - qwen2.5:3b   : minimum viable, struggles past ~4 tools
    """
    from google.adk.models.lite_llm import LiteLlm
    from shopaiholic.agents import root_agent
    from shopaiholic.agents.meal_planner import meal_planner
    from shopaiholic.agents.store_finder import store_finder

    model = LiteLlm(model="ollama/qwen3:8b")

    for agent in [root_agent, meal_planner, store_finder]:
        agent.model = model


def _patch_agents_for_groq() -> None:
    """Swap all agents to a Groq-hosted model via LiteLlm.

    Default: openai/gpt-oss-20b — OpenAI's open model on Groq's hardware, designed
    for OpenAI-compatible tool calling, very fast.
    Alternatives:
      - meta-llama/llama-4-scout-17b-16e-instruct : newer Llama, strong tool use
      - llama-3.3-70b-versatile                    : powerful but sometimes drops
                                                     out of OpenAI tool format
      - llama-3.1-8b-instant                       : smaller/faster
    """
    import os
    from google.adk.models.lite_llm import LiteLlm
    from shopaiholic.agents import root_agent
    from shopaiholic.agents.meal_planner import meal_planner
    from shopaiholic.agents.store_finder import store_finder

    if not os.environ.get("GROQ_API_KEY"):
        raise RuntimeError("GROQ_API_KEY is not set. Add it to .env.")

    # num_retries lets LiteLLM honor the server-provided retry-after header,
    # so when Groq's TPM bucket fills up we just wait the suggested seconds
    # and continue rather than crashing.
    model = LiteLlm(
        model="groq/meta-llama/llama-4-scout-17b-16e-instruct",
        num_retries=5,
    )

    for agent in [root_agent, meal_planner, store_finder]:
        agent.model = model


async def run_chat(local: bool = False, groq: bool = False) -> None:
    runner = _build_runner(local=local, groq=groq)

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
    groq_mode = "--groq" in sys.argv
    asyncio.run(run_chat(local=local_mode, groq=groq_mode))
