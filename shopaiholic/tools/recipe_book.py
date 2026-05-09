"""Mock recipe book tool with structured ingredients and stable IDs.

The tool returns recipes from a static curated list AND from the user's
downloaded_recipes store (recipes the meal_planner has invented or sourced
externally and saved via save_recipe).

user_affinity scale (descriptive so LLMs can reason over it):
  "loved"    — contains an ingredient/tag the user explicitly likes
  "liked"    — partial keyword overlap with user likes
  "neutral"  — no strong signal either way
  "disliked" — contains something the user dislikes (not an allergen)
  "allergic" — contains a known allergen; must be excluded from the plan
"""

from __future__ import annotations

from typing import Any

from shopaiholic.tools.downloaded_recipes import load_downloaded_recipes


# Static curated recipes. Each recipe has a stable `id` plus structured
# `ingredients` so the deterministic aggregator can sum them precisely.
RECIPES: list[dict[str, Any]] = [
    {
        "id": "r001",
        "name": "Spicy Chicken Breasts with Rice and Broccoli",
        "recipe": "Season 150g chicken breasts with paprika, garlic, cayenne. Grill 6-8 min per side. Cook 80g rice. Steam 250g broccoli 5 min.",
        "ingredients": [
            {"name": "chicken breast", "quantity": 150.0, "unit": "g"},
            {"name": "rice",            "quantity": 80.0,  "unit": "g"},
            {"name": "broccoli",        "quantity": 250.0, "unit": "g"},
        ],
        "tags": ["protein", "bulking", "chicken", "broccoli", "rice", "spicy"],
    },
    {
        "id": "r002",
        "name": "Bulking Broccoli Beef Stir Fry",
        "recipe": "Slice 200g beef sirloin thin. Stir fry with 300g broccoli, garlic, soy sauce 5 min. Serve over 100g cooked white rice.",
        "ingredients": [
            {"name": "beef sirloin", "quantity": 200.0, "unit": "g"},
            {"name": "broccoli",     "quantity": 300.0, "unit": "g"},
            {"name": "rice",         "quantity": 100.0, "unit": "g"},
        ],
        "tags": ["protein", "bulking", "beef", "broccoli", "rice"],
    },
    {
        "id": "r003",
        "name": "High Protein Broccoli Chicken Casserole",
        "recipe": "Mix 200g cooked chicken, 400g steamed broccoli, 100g Greek yogurt, 50g cheddar. Bake 20 min at 180C.",
        "ingredients": [
            {"name": "chicken breast", "quantity": 200.0, "unit": "g"},
            {"name": "broccoli",       "quantity": 400.0, "unit": "g"},
            {"name": "greek yogurt",   "quantity": 100.0, "unit": "g"},
            {"name": "cheddar",        "quantity": 50.0,  "unit": "g"},
        ],
        "tags": ["protein", "chicken", "broccoli", "healthy", "dairy"],
    },
    {
        "id": "r004",
        "name": "Overnight Oats with Banana",
        "recipe": "Mix 80g oats, 200ml milk, 1 banana sliced, 1 tbsp honey. Refrigerate overnight.",
        "ingredients": [
            {"name": "oats",   "quantity": 80.0,  "unit": "g"},
            {"name": "milk",   "quantity": 200.0, "unit": "ml"},
            {"name": "banana", "quantity": 1.0,   "unit": "each"},
            {"name": "honey",  "quantity": 15.0,  "unit": "ml"},
        ],
        "tags": ["breakfast", "healthy", "budget", "vegetarian", "dairy", "gluten"],
    },
    {
        "id": "r005",
        "name": "Lentil Vegetable Soup",
        "recipe": "Sauté onion, carrot, celery. Add 200g red lentils, 1L vegetable stock, cumin, paprika. Simmer 25 min.",
        "ingredients": [
            {"name": "red lentils",     "quantity": 200.0,  "unit": "g"},
            {"name": "onion",           "quantity": 1.0,    "unit": "each"},
            {"name": "carrot",          "quantity": 2.0,    "unit": "each"},
            {"name": "vegetable stock", "quantity": 1000.0, "unit": "ml"},
        ],
        "tags": ["healthy", "budget", "vegetarian", "saving_money", "soup", "vegan"],
    },
    {
        "id": "r006",
        "name": "Scrambled Eggs with Toast",
        "recipe": "Whisk 3 eggs with splash of milk, salt, pepper. Cook over low heat. Serve on 2 slices toasted bread.",
        "ingredients": [
            {"name": "eggs",  "quantity": 3.0,  "unit": "each"},
            {"name": "bread", "quantity": 2.0,  "unit": "each"},
            {"name": "milk",  "quantity": 30.0, "unit": "ml"},
        ],
        "tags": ["breakfast", "budget", "quick", "saving_money", "eggs", "gluten", "dairy"],
    },
    {
        "id": "r007",
        "name": "Grilled Salmon with Sweet Potato",
        "recipe": "Season 150g salmon. Grill 4 min per side. Roast 200g sweet potato cubes at 200C for 25 min.",
        "ingredients": [
            {"name": "salmon",       "quantity": 150.0, "unit": "g"},
            {"name": "sweet potato", "quantity": 200.0, "unit": "g"},
        ],
        "tags": ["healthy", "longevity", "fish", "protein", "salmon"],
    },
    {
        "id": "r008",
        "name": "Greek Yogurt Parfait",
        "recipe": "Layer 200g Greek yogurt, 50g granola, mixed berries. Drizzle with honey.",
        "ingredients": [
            {"name": "greek yogurt", "quantity": 200.0, "unit": "g"},
            {"name": "granola",      "quantity": 50.0,  "unit": "g"},
            {"name": "berries",      "quantity": 80.0,  "unit": "g"},
        ],
        "tags": ["breakfast", "snack", "healthy", "protein", "dairy", "gluten"],
    },
    {
        "id": "r009",
        "name": "Avocado Toast with Poached Eggs",
        "recipe": "Toast 2 slices sourdough. Mash 1 avocado with lemon juice, salt. Top with 2 poached eggs.",
        "ingredients": [
            {"name": "bread",   "quantity": 2.0, "unit": "each"},
            {"name": "avocado", "quantity": 1.0, "unit": "each"},
            {"name": "eggs",    "quantity": 2.0, "unit": "each"},
        ],
        "tags": ["breakfast", "healthy", "avocado", "eggs", "gluten"],
    },
    {
        "id": "r010",
        "name": "Steak with Roasted Vegetables",
        "recipe": "Season 200g ribeye with salt, pepper, garlic. Sear 3 min per side. Roast 300g mixed vegetables at 200C for 30 min.",
        "ingredients": [
            {"name": "ribeye steak",     "quantity": 200.0, "unit": "g"},
            {"name": "mixed vegetables", "quantity": 300.0, "unit": "g"},
        ],
        "tags": ["protein", "bulking", "steak", "beef", "healthy"],
    },
]


def _searchable(recipe: dict) -> str:
    return (recipe["name"] + " " + " ".join(recipe["tags"])).lower()


def _affinity(searchable: str, ingredient_names: list[str], likes: list[str], allergies: list[str]) -> str:
    """Compute a descriptive affinity label for a single recipe."""
    lower_allergies = [a.lower() for a in allergies]
    lower_likes = [l.lower() for l in likes]
    haystack = searchable + " " + " ".join(ingredient_names).lower()

    if any(allergen in haystack for allergen in lower_allergies):
        return "allergic"

    matched_likes = [like for like in lower_likes if like in haystack]
    if len(matched_likes) >= 2:
        return "loved"
    if len(matched_likes) == 1:
        return "liked"
    return "neutral"


def recipe_book(
    keywords: list[str],
    likes: list[str] | None = None,
    allergies: list[str] | None = None,
) -> list[dict]:
    """Find recipes matching keywords, rated by user affinity.

    Searches both the curated RECIPES list and any recipes the user
    has previously saved via save_recipe.

    Args:
        keywords: Search terms, e.g. ["protein", "bulking", "chicken"].
        likes: Foods the user enjoys. Drives the user_affinity rating.
        allergies: Known allergens. Recipes containing these are
                   marked "allergic" — the Meal Planner must exclude them.

    Returns:
        List of recipe dicts ordered by relevance, each containing:
          - id, name, recipe (description), ingredients (structured), tags
          - user_affinity: "loved" | "liked" | "neutral" | "allergic"
    """
    _likes = likes or []
    _allergies = allergies or []
    lower_kw = [k.lower() for k in keywords]

    all_recipes = RECIPES + load_downloaded_recipes()

    scored = []
    for r in all_recipes:
        searchable = _searchable(r)
        ingredient_names = [i["name"] for i in r.get("ingredients", [])]
        kw_score = sum(1 for kw in lower_kw if kw in searchable or any(kw in n for n in ingredient_names))
        if not lower_kw or kw_score > 0:
            recipe = dict(r)
            recipe["user_affinity"] = _affinity(searchable, ingredient_names, _likes, _allergies)
            scored.append((kw_score, recipe))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = [r for _, r in scored]

    if not results:
        fallback = []
        for r in all_recipes[:3]:
            recipe = dict(r)
            recipe["user_affinity"] = _affinity(_searchable(r), [i["name"] for i in r.get("ingredients", [])], _likes, _allergies)
            fallback.append(recipe)
        return fallback

    return results
