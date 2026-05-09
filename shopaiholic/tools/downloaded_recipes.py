"""User-specific recipe storage and the save_recipe tool.

When the meal_planner invents or sources a recipe that isn't in the
curated recipe_book, it MUST save it via save_recipe before referencing
it in the meal plan. This guarantees every recipe_id in the plan
resolves downstream (in the deterministic aggregator).

Persisted to ~/.shopaiholic/downloaded_recipes.json so users build up a
personalised collection over multiple sessions.
"""

from __future__ import annotations

import json
import threading
import uuid
from pathlib import Path
from typing import Any

DEFAULT_PATH = Path.home() / ".shopaiholic" / "downloaded_recipes.json"

_lock = threading.Lock()


def _ensure_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("[]", encoding="utf-8")


def load_downloaded_recipes(path: Path | str = DEFAULT_PATH) -> list[dict[str, Any]]:
    """Load all recipes the user has saved. Used by recipe_book."""
    p = Path(path)
    _ensure_file(p)
    with _lock:
        with p.open("r", encoding="utf-8") as fh:
            return json.load(fh)


def save_recipe(
    name: str,
    recipe: str,
    ingredients: list[dict],
    tags: list[str],
) -> dict:
    """Save a new recipe to the user's downloaded recipe collection.

    Use this when you want to reference a recipe in a meal plan but it
    isn't in the curated recipe_book. The returned id can then be used
    in the MealReference.recipe_id field.

    Args:
        name: Display name, e.g. "Spicy Chicken with Rice and Broccoli".
        recipe: Cooking instructions in 1-3 sentences.
        ingredients: List of {"name": str, "quantity": float, "unit": str}.
                     Names should be lowercase, singular, no modifiers.
                     Units: g, kg, ml, l, or "each".
        tags: Search tags, e.g. ["protein", "bulking", "chicken"].

    Returns:
        {"id": "<new_id>", "name": "<name>"} — use the id in your MealPlan.

    Example:
        save_recipe(
            name="Lemon Garlic Salmon",
            recipe="Season 200g salmon with lemon and garlic. Bake 12 min at 200C.",
            ingredients=[
                {"name": "salmon", "quantity": 200.0, "unit": "g"},
                {"name": "lemon",  "quantity": 1.0,   "unit": "each"},
            ],
            tags=["healthy", "fish", "salmon", "longevity"],
        )
    """
    p = Path(DEFAULT_PATH)
    _ensure_file(p)

    new_id = f"d{uuid.uuid4().hex[:8]}"
    new_recipe = {
        "id": new_id,
        "name": name,
        "recipe": recipe,
        "ingredients": ingredients,
        "tags": tags,
    }

    with _lock:
        with p.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        data.append(new_recipe)
        tmp = p.with_suffix(".json.tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        tmp.replace(p)

    return {"id": new_id, "name": name}
