"""Pure-Python store comparison.

Reads the shopping list and store list from session state (saved by
the aggregator and store_finder respectively), queries the supermarket
API for each (store, ingredient) pair, and returns the cheapest store.

Zero LLM calls — purely deterministic.
"""

from __future__ import annotations

from typing import Any

from google.adk.tools.tool_context import ToolContext

from shopaiholic.tools.supermarket_api import supermarket_api_tools


def _normalise(s: str) -> str:
    return s.lower().strip()


def _product_matches(ingredient: str, product_name: str) -> bool:
    return _normalise(ingredient) in _normalise(product_name)


def compute_cheapest_store(tool_context: ToolContext | None = None) -> dict[str, Any]:
    """Find the cheapest store for the current shopping list.

    Reads inputs from session state:
      - state["shopping_list"]   (saved by aggregate_shopping_list)
      - state["stores"]          (saved by find_stores via output_key="stores")

    Returns:
        {
          "cheapest_store": {"name": str, "address": str, "total_eur": float},
          "items":          [{"ingredient": str, "product": str, "price_eur": float}, ...],
          "all_stores":     [{"name": str, "address": str, "total_eur": float}, ...],
          "missing":        {store_address: [unavailable_ingredient, ...]}
        }
    """
    if tool_context is None:
        return {"error": "tool_context is required (ADK injects it automatically)."}

    shopping_list = tool_context.state.get("shopping_list", []) or []
    stores_state = tool_context.state.get("stores", {}) or {}

    # find_stores writes a StoreList object → state["stores"] = {"stores": [...]}
    stores = stores_state.get("stores", []) if isinstance(stores_state, dict) else stores_state

    if not stores or not shopping_list:
        return {"cheapest_store": None, "items": [], "all_stores": [], "missing": {}}

    per_store_totals: list[dict] = []
    per_store_items: dict[str, list[dict]] = {}
    missing: dict[str, list[str]] = {}

    for store in stores:
        address = store["address"] if isinstance(store, dict) else store.address
        name = store["name"] if isinstance(store, dict) else store.name
        total = 0.0
        items: list[dict] = []
        unavailable: list[str] = []

        for shop_item in shopping_list:
            ingredient = shop_item["ingredient"] if isinstance(shop_item, dict) else shop_item.ingredient
            response = supermarket_api_tools(address=address, food_item=ingredient)
            products = response.get("items", [])

            matching = [p for p in products if _product_matches(ingredient, p["name"])] or products

            if not matching:
                unavailable.append(ingredient)
                continue

            cheapest = min(matching, key=lambda p: float(p["price"]))
            total += float(cheapest["price"])
            items.append({
                "ingredient": ingredient,
                "product": cheapest["name"],
                "price_eur": float(cheapest["price"]),
            })

        per_store_totals.append({"name": name, "address": address, "total_eur": round(total, 2)})
        per_store_items[address] = items
        if unavailable:
            missing[address] = unavailable

    candidates = [s for s in per_store_totals if s["address"] not in missing] or per_store_totals
    cheapest = min(candidates, key=lambda s: s["total_eur"])
    cheapest_items = per_store_items[cheapest["address"]]
    per_store_totals.sort(key=lambda s: s["total_eur"])

    return {
        "cheapest_store": cheapest,
        "items": cheapest_items,
        "all_stores": per_store_totals,
        "missing": missing,
    }
