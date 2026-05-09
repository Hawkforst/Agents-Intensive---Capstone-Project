"""Configuration: env loading, model map, retry options."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from google.genai import types

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


MODEL_MAP = {
    "meal_orchestrator": "gemini-2.5-flash",
    "meal_planner": "gemini-2.5-pro",
    "ingredient_aggregator": "gemini-2.5-flash",
    "store_finder": "gemini-2.5-flash-lite",
    "store_buyer": "gemini-2.5-flash",
}


RETRY_CONFIG = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)


def require_google_api_key() -> str:
    key = os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError(
            "GOOGLE_API_KEY is not set. Copy .env.example to .env and fill it in."
        )
    return key


def google_maps_api_key() -> str | None:
    return os.environ.get("GOOGLE_MAPS_API_KEY") or None
