"""Pure-Python shopping list aggregator.

Reads the meal plan from session state (saved by meal_planner via
output_key="meal_plan"), the pantry from the LocalMemoryStore, and
user allergies from preferences. Writes the resulting shopping list
back to state["shopping_list"] for downstream tools to consume.

Zero LLM calls — purely deterministic arithmetic.
"""

from __future__ import annotations

import math
from typing import Any

from google.adk.tools.tool_context import ToolContext

from shopaiholic.memory import memory_store
from shopaiholic.tools.downloaded_recipes import load_downloaded_recipes
from shopaiholic.tools.recipe_book import RECIPES

# Conversion factors to canonical units (g for weight, ml for volume).
_TO_GRAMS = {
    "g": 1.0, "gram": 1.0, "grams": 1.0,
    "kg": 1000.0, "kilogram": 1000.0, "kilograms": 1000.0,
}
_TO_ML = {
    "ml": 1.0, "milliliter": 1.0, "milliliters": 1.0,
    "l": 1000.0, "liter": 1000.0, "liters": 1000.0, "litre": 1000.0,
}


def _canonical(quantity: float, unit: str) -> tuple[float, str]:
    u = unit.lower().strip()
    if u in _TO_GRAMS:
        return quantity * _TO_GRAMS[u], "g"
    if u in _TO_ML:
        return quantity * _TO_ML[u], "ml"
    if u in ("each", "ea", "pcs", "piece", "pieces"):
        return quantity, "each"
    return quantity, u


def _normalise_name(name: str) -> str:
    n = name.lower().strip()
    if n.endswith("s") and len(n) > 3:
        n = n[:-1]
    return n


def _round_up(quantity: float, granularity: float) -> float:
    if granularity <= 0:
        return quantity
    return math.ceil(quantity / granularity) * granularity


def _build_recipe_index() -> dict[str, dict]:
    return {r["id"]: r for r in (RECIPES + load_downloaded_recipes())}


def aggregate_shopping_list(
    round_to_grams: float = 100.0,
    round_to_ml: float = 100.0,
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Build a consolidated shopping list from the current meal plan.

    Reads inputs from session state and persistent memory:
      - state["meal_plan"]              (saved by meal_planner)
      - persistent pantry               (saved by food_storage)
      - persistent user allergies       (saved by user_preferences)

    Writes state["shopping_list"] and returns a summary dict.

    Args:
        round_to_grams: Granularity for rounding up gram quantities.
        round_to_ml: Granularity for rounding up ml quantities.
        tool_context: Injected by ADK — do not pass manually.

    Returns:
        {
          "shopping_list": [{"ingredient": str, "quantity": float, "unit": str}, ...],
          "skipped_for_allergy": [str, ...],
          "missing_recipe_ids": [str, ...]
        }
    """
    if tool_context is None:
        return {"error": "tool_context is required (ADK injects it automatically)."}

    meal_plan = tool_context.state.get("meal_plan", {}) or {}
    user_id = tool_context.user_id or "default_user"
    pantry = memory_store.get_pantry(user_id)
    prefs = memory_store.get_prefs(user_id)
    allergies = [a.lower().strip() for a in prefs.get("allergies", [])]

    recipe_index = _build_recipe_index()
    totals: dict[tuple[str, str], float] = {}
    missing: list[str] = []

    for day in meal_plan.get("days", []) if isinstance(meal_plan, dict) else []:
        for slot in ("breakfast", "lunch", "dinner", "snacks"):
            meal = day.get(slot)
            if not meal:
                continue
            recipe_id = meal.get("recipe_id") if isinstance(meal, dict) else None
            if not recipe_id:
                continue
            if recipe_id not in recipe_index:
                missing.append(recipe_id)
                continue
            for ing in recipe_index[recipe_id].get("ingredients", []):
                name = _normalise_name(ing["name"])
                qty, cunit = _canonical(float(ing["quantity"]), ing["unit"])
                key = (name, cunit)
                totals[key] = totals.get(key, 0.0) + qty

    # Subtract pantry quantities
    for entry in pantry:
        name = _normalise_name(entry["name"])
        qty, cunit = _canonical(float(entry["quantity"]), entry["unit"])
        key = (name, cunit)
        if key in totals:
            totals[key] = max(0.0, totals[key] - qty)

    # Filter allergens
    skipped: list[str] = []
    for (name, cunit) in list(totals.keys()):
        if any(allergen and allergen in name for allergen in allergies):
            skipped.append(name)
            del totals[(name, cunit)]

    # Round up to friendly pack sizes
    shopping_list = []
    for (name, cunit), qty in sorted(totals.items()):
        if qty <= 0:
            continue
        if cunit == "g":
            qty = _round_up(qty, round_to_grams)
        elif cunit == "ml":
            qty = _round_up(qty, round_to_ml)
        else:
            qty = math.ceil(qty)
        shopping_list.append({"ingredient": name, "quantity": qty, "unit": cunit})

    tool_context.state["shopping_list"] = shopping_list

    return {
        "shopping_list": shopping_list,
        "skipped_for_allergy": skipped,
        "missing_recipe_ids": missing,
    }
