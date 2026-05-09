"""One-shot smoke test against the configured model.

Modes:
  Gemini (default):  .venv/bin/python scripts/smoke_test.py
  Local Ollama:      .venv/bin/python scripts/smoke_test.py --local

Streams every agent event to stdout as it arrives, with timestamps.
"""

from __future__ import annotations

import asyncio
import json
import sys
import time
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


def _ts(start: float) -> str:
    """Seconds since start, zero-padded to 6.2f."""
    return f"{time.monotonic() - start:6.2f}s"


def _truncate(value: str, limit: int = 400) -> str:
    return value if len(value) <= limit else value[:limit] + f"  ... ({len(value) - limit} more chars)"


def _log(start: float, msg: str, *, end: str = "\n") -> None:
    print(f"[{_ts(start)}] {msg}", end=end, flush=True)


async def main() -> None:
    local_mode = "--local" in sys.argv
    start = time.monotonic()

    _log(start, f"Mode: {'Local Ollama' if local_mode else 'Gemini'}")
    _log(start, "Building runner ...")
    runner = _build_runner(local=local_mode)

    _log(start, "Creating session ...")
    await runner.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID,
    )

    _log(start, "")
    _log(start, "USER ▶ " + CANNED_MESSAGE)
    _log(start, "─" * 80)

    message = types.Content(role="user", parts=[types.Part(text=CANNED_MESSAGE)])

    event_count = 0
    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=message,
    ):
        event_count += 1
        author = getattr(event, "author", "?")
        header = f"EVENT {event_count:2} ({author})"
        _log(start, header)

        if event.content and event.content.parts:
            for part in event.content.parts:
                if getattr(part, "text", None):
                    _log(start, f"  TEXT │ {_truncate(part.text)}")
                if getattr(part, "function_call", None):
                    fc = part.function_call
                    args = dict(fc.args) if fc.args else {}
                    _log(start, f"  CALL │ {fc.name}({_truncate(json.dumps(args, default=str), 300)})")
                if getattr(part, "function_response", None):
                    fr = part.function_response
                    response_str = _truncate(json.dumps(fr.response, default=str), 300)
                    _log(start, f"  RESP │ {fr.name} ⇒ {response_str}")

    _log(start, "─" * 80)
    _log(start, f"Done. Total events: {event_count}")


if __name__ == "__main__":
    asyncio.run(main())
