"""One-shot smoke test against qwen2.5:3b via Ollama.

Sends a canned message that gives the orchestrator everything it needs
to (potentially) walk through the full workflow. Prints every event so
we can see exactly where things succeed or break.

Run:
    .venv/bin/python scripts/smoke_test.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from google.genai import types

from shopaiholic.app import APP_NAME, SESSION_ID, USER_ID, _build_runner

CANNED_MESSAGE = (
    "Plan 2 days of dinners for me. I'm bulking, allergic to peanuts, "
    "I like steak. My address is Long Street 321, Prague, max distance 5 km. "
    "I have 200g chicken breast at home. Skip the confirmations and just go "
    "through the whole pipeline once."
)


async def main() -> None:
    runner = _build_runner(local=True)

    await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    print(f"USER: {CANNED_MESSAGE}\n")
    print("=" * 80)

    message = types.Content(role="user", parts=[types.Part(text=CANNED_MESSAGE)])

    event_count = 0
    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=message,
    ):
        event_count += 1
        author = getattr(event, "author", "?")
        print(f"\n--- EVENT {event_count} (author={author}) ---")

        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    print(f"[TEXT] {part.text}")
                if hasattr(part, "function_call") and part.function_call:
                    fc = part.function_call
                    print(f"[TOOL CALL] {fc.name}({dict(fc.args) if fc.args else {}})")
                if hasattr(part, "function_response") and part.function_response:
                    fr = part.function_response
                    response_str = str(fr.response)[:300]
                    print(f"[TOOL RESPONSE] {fr.name} -> {response_str}")

    print("\n" + "=" * 80)
    print(f"Total events: {event_count}")


if __name__ == "__main__":
    asyncio.run(main())
