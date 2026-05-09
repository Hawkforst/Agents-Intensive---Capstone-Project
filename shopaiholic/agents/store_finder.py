"""Store Finder sub-agent.

Uses Google Maps MCP tools when GOOGLE_MAPS_API_KEY is set.
Falls back to a stub list of mock stores (Happyville) when no key is available,
so the rest of the pipeline can still run end-to-end in offline/dev mode.
"""

from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

from shopaiholic.config import MODEL_MAP, RETRY_CONFIG, google_maps_api_key
from shopaiholic.models import StoreList
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
5. Return the results sorted by distance ascending as JSON in this exact shape:
   {"stores": [{"name": ..., "address": ..., "distance_km": ...}, ...]}
"""

_INSTRUCTION_STUB = """You are a store locator running in offline/demo mode.
Return exactly these two demo stores:
  - Albert at "Happyville 21 Albert", 1.2 km
  - Billa at "Happyville 113 Billa", 2.8 km
"""


if google_maps_api_key():
    # Real mode: agent needs the maps tools, so output_schema is unavailable
    # (Gemini API limitation). The agent emits free text JSON and the
    # orchestrator/downstream parses it.
    # TODO: split into a "stores_lookup" agent (with tools) + "stores_format"
    # agent (with output_schema) for stricter contract.
    store_finder = LlmAgent(
        name="store_finder",
        model=Gemini(model=MODEL_MAP["store_finder"], http_options={"retry_options": RETRY_CONFIG}),
        instruction=_INSTRUCTION_WITH_MAPS,
        tools=[user_preferences, _maps],
    )
else:
    # Stub mode: no tools needed, so output_schema can enforce a clean
    # StoreList JSON that compute_cheapest_store consumes from state.
    store_finder = LlmAgent(
        name="store_finder",
        model=Gemini(model=MODEL_MAP["store_finder"], http_options={"retry_options": RETRY_CONFIG}),
        instruction=_INSTRUCTION_STUB,
        output_schema=StoreList,
        output_key="stores",
    )
