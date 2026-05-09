"""Pure-Python store comparison.

Given a shopping list and a list of stores, query the supermarket API
for each (store, ingredient) pair, pick the cheapest matching product,
sum totals per store, and identify the cheapest store overall.

Zero LLM calls — purely deterministic. The only fuzzy step is matching
ingredient names against vendor product names; we use simple substring
matching with normalisation.
"""

from __future__ import annotations

from typing import Any

from shopaiholic.tools.supermarket_api import supermarket_api_tools


def _normalise(s: str) -> str:
    return s.lower().strip()


def _product_matches(ingredient: str, product_name: str) -> bool:
    """True if the product name plausibly contains the ingredient."""
    return _normalise(ingredient) in _normalise(product_name)


def compute_cheapest_store(
    shopping_list: list[dict],
    stores: list[dict],
) -> dict[str, Any]:
    """Find the cheapest store for the given shopping list.

    Args:
        shopping_list: List of {"ingredient": str, "quantity": float, "unit": str}.
        stores: List of {"name": str, "address": str, "distance_km": float}.

    Returns:
        {
            "cheapest_store": {"name": str, "address": str, "total_eur": float},
            "items":         [{"ingredient": str, "product": str, "price_eur": float}, ...],
            "all_stores":    [{"name": str, "address": str, "total_eur": float}, ...],
            "missing":       {store_address: [unavailable_ingredient, ...]}
        }
    """
    if not stores or not shopping_list:
        return {
            "cheapest_store": None,
            "items": [],
            "all_stores": [],
            "missing": {},
        }

    per_store_totals: list[dict] = []
    per_store_items: dict[str, list[dict]] = {}
    missing: dict[str, list[str]] = {}

    for store in stores:
        address = store["address"]
        total = 0.0
        items: list[dict] = []
        unavailable: list[str] = []

        for shop_item in shopping_list:
            ingredient = shop_item["ingredient"]
            response = supermarket_api_tools(address=address, food_item=ingredient)
            products = response.get("items", [])

            matching = [
                p for p in products
                if _product_matches(ingredient, p["name"])
            ] or products  # fall back to anything returned for the keyword

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

        per_store_totals.append({
            "name": store["name"],
            "address": address,
            "total_eur": round(total, 2),
        })
        per_store_items[address] = items
        if unavailable:
            missing[address] = unavailable

    # Stores that have everything available; tiebreaker: lower distance
    candidates = [
        s for s in per_store_totals
        if s["address"] not in missing
    ] or per_store_totals

    cheapest = min(candidates, key=lambda s: s["total_eur"])
    cheapest_items = per_store_items[cheapest["address"]]

    per_store_totals.sort(key=lambda s: s["total_eur"])

    return {
        "cheapest_store": cheapest,
        "items": cheapest_items,
        "all_stores": per_store_totals,
        "missing": missing,
    }
