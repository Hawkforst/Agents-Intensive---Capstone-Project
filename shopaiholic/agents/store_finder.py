"""Store Finder sub-agent.

Uses Google Maps MCP tools when GOOGLE_MAPS_API_KEY is set.
Falls back to a stub list of mock stores (Happyville) when no key is available,
so the rest of the pipeline can still run end-to-end in offline/dev mode.
"""

from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

from shopaiholic.config import MODEL_MAP, RETRY_CONFIG, google_maps_api_key
from shopaiholic.tools import user_preferences
from shopaiholic.tools.maps_mcp import build_maps_toolset

_maps = build_maps_toolset()

_INSTRUCTION_WITH_MAPS = """You are a store locator. Your task is to find supermarkets near the
user's address using the maps tools available to you.

Steps:
1. Call user_preferences(action="retrieve") to get the user's address and max_distance.
2. Geocode the address using maps_geocode.
3. Search for nearby supermarkets using maps_nearby_search with type="supermarket" and
   radius = max_distance * 1000 (metres).
4. For each result, call maps_place_details to get the full formatted address.
5. Return the results sorted by distance ascending.

Output format — strict JSON, no extra text:
{
  "stores": [
    {"name": "Albert", "address": "Big Square 123, Prague", "distance_km": 1.2},
    {"name": "Lidl",   "address": "E55 456, Prague",        "distance_km": 3.5}
  ]
}
"""

_INSTRUCTION_STUB = """You are a store locator running in offline/demo mode (no Maps API key).
Return the following hardcoded demo store list without calling any tools.

Output this exact JSON:
{
  "stores": [
    {"name": "Albert", "address": "Happyville 21 Albert", "distance_km": 1.2},
    {"name": "Billa",  "address": "Happyville 113 Billa", "distance_km": 2.8}
  ]
}
"""

_tools = [user_preferences] + ([_maps] if _maps else [])
_instruction = _INSTRUCTION_WITH_MAPS if google_maps_api_key() else _INSTRUCTION_STUB

store_finder = LlmAgent(
    name="store_finder",
    model=Gemini(model=MODEL_MAP["store_finder"], http_options={"retry_options": RETRY_CONFIG}),
    instruction=_instruction,
    tools=_tools,
)
