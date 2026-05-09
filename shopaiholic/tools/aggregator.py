"""Pure-Python shopping list aggregator.

Sums ingredient requirements across a meal plan, subtracts what is
already in the pantry, filters allergens, and rounds quantities up
to a supermarket-friendly granularity.

Zero LLM calls — purely deterministic arithmetic so we can never
miscount, drop, or hallucinate quantities.
"""

from __future__ import annotations

import math
from typing import Any

from shopaiholic.tools.recipe_book import RECIPES
from shopaiholic.tools.downloaded_recipes import load_downloaded_recipes


# Conversion factors to canonical units (g for weight, ml for volume).
# Items in "each" stay as their own canonical unit.
_TO_GRAMS = {
    "g": 1.0, "gram": 1.0, "grams": 1.0,
    "kg": 1000.0, "kilogram": 1000.0, "kilograms": 1000.0,
}
_TO_ML = {
    "ml": 1.0, "milliliter": 1.0, "milliliters": 1.0,
    "l": 1000.0, "liter": 1000.0, "liters": 1000.0, "litre": 1000.0,
}


def _canonical(quantity: float, unit: str) -> tuple[float, str]:
    """Convert a quantity to its canonical unit (g, ml, or each)."""
    u = unit.lower().strip()
    if u in _TO_GRAMS:
        return quantity * _TO_GRAMS[u], "g"
    if u in _TO_ML:
        return quantity * _TO_ML[u], "ml"
    if u in ("each", "ea", "pcs", "piece", "pieces"):
        return quantity, "each"
    # Unknown unit — fall through and treat as canonical itself.
    return quantity, u


def _normalise_name(name: str) -> str:
    """Lowercase, strip, drop trailing 's' for plural matching."""
    n = name.lower().strip()
    if n.endswith("s") and len(n) > 3:
        n = n[:-1]
    return n


def _round_up(quantity: float, unit: str, granularity: float) -> float:
    """Round quantity up to the next multiple of granularity."""
    if granularity <= 0:
        return quantity
    return math.ceil(quantity / granularity) * granularity


def _build_recipe_index() -> dict[str, dict]:
    """Combine static + downloaded recipes into an id-indexed lookup."""
    return {r["id"]: r for r in (RECIPES + load_downloaded_recipes())}


def aggregate_shopping_list(
    meal_plan: dict,
    pantry: list[dict] | None = None,
    allergies: list[str] | None = None,
    round_to_grams: float = 100.0,
    round_to_ml: float = 100.0,
) -> dict[str, Any]:
    """Build a consolidated shopping list from a meal plan.

    Args:
        meal_plan: The MealPlan dict produced by meal_planner. Shape:
            {"days": [{"day": 1, "breakfast": {...}, "dinner": {...}, ...}, ...]}
            Each meal slot is either null or {"name": str, "recipe_id": str}.
        pantry: List of {"name": str, "quantity": float, "unit": str} from
                food_storage. Quantities are subtracted from totals.
        allergies: List of allergen strings. Any aggregated ingredient
                   whose name contains an allergen substring is dropped
                   AND reported in the "skipped_for_allergy" list.
        round_to_grams: Granularity for rounding up gram quantities.
        round_to_ml: Granularity for rounding up ml quantities.

    Returns:
        {
            "shopping_list": [{"ingredient": str, "quantity": float, "unit": str}, ...],
            "skipped_for_allergy": [str, ...],
            "missing_recipe_ids": [str, ...]   # ids that didn't resolve
        }
    """
    pantry = pantry or []
    allergies = [a.lower().strip() for a in (allergies or [])]
    recipe_index = _build_recipe_index()

    # totals[(name, canonical_unit)] = quantity_in_canonical
    totals: dict[tuple[str, str], float] = {}
    missing: list[str] = []

    for day in meal_plan.get("days", []):
        for slot in ("breakfast", "lunch", "dinner", "snacks"):
            meal = day.get(slot)
            if not meal:
                continue
            recipe_id = meal.get("recipe_id")
            if not recipe_id or recipe_id not in recipe_index:
                if recipe_id:
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
    for (name, _cunit) in list(totals.keys()):
        if any(allergen and allergen in name for allergen in allergies):
            skipped.append(name)
            del totals[(name, _cunit)]

    # Round up to friendly pack sizes and emit
    shopping_list = []
    for (name, cunit), qty in sorted(totals.items()):
        if qty <= 0:
            continue
        if cunit == "g":
            qty = _round_up(qty, cunit, round_to_grams)
        elif cunit == "ml":
            qty = _round_up(qty, cunit, round_to_ml)
        else:
            qty = math.ceil(qty)
        shopping_list.append({"ingredient": name, "quantity": qty, "unit": cunit})

    return {
        "shopping_list": shopping_list,
        "skipped_for_allergy": skipped,
        "missing_recipe_ids": missing,
    }
