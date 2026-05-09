"""Mock recipe book tool.

Returns a small set of hardcoded recipes filtered by keywords, with a
per-recipe user_affinity rating so the Meal Planner can prioritise or
exclude recipes based on the user's stated preferences.

user_affinity scale (descriptive so LLMs can reason over it):
  "loved"    — contains an ingredient/tag the user explicitly likes
  "liked"    — partial keyword overlap with user likes
  "neutral"  — no strong signal either way
  "disliked" — contains something the user dislikes (not an allergen)
  "allergic" — contains a known allergen; must be excluded from the plan

Replace RECIPES with a real API call when ready.
"""

from __future__ import annotations

RECIPES = [
    {
        "name": "Spicy Chicken Breasts with Rice and Broccoli",
        "recipe": "Season 150g chicken breasts with paprika, garlic, cayenne. Grill 6-8 min per side. Cook 80g rice. Steam 250g broccoli 5 min. Serve with hot sauce.",
        "ingredients": "150g chicken breasts, 80g rice, 250g broccoli, paprika, garlic, cayenne",
        "tags": ["protein", "bulking", "chicken", "broccoli", "rice", "spicy"],
    },
    {
        "name": "Bulking Broccoli Beef Stir Fry",
        "recipe": "Slice 200g beef sirloin thin. Stir fry with 300g broccoli, garlic, soy sauce 5 min. Serve over 100g cooked white rice.",
        "ingredients": "200g beef sirloin, 300g broccoli, 100g rice, soy sauce, garlic",
        "tags": ["protein", "bulking", "beef", "broccoli", "rice"],
    },
    {
        "name": "High Protein Broccoli Chicken Casserole",
        "recipe": "Mix 200g cooked chicken, 400g steamed broccoli, 100g Greek yogurt, 50g cheddar. Bake 20 min at 180C.",
        "ingredients": "200g chicken, 400g broccoli, 100g Greek yogurt, 50g cheddar",
        "tags": ["protein", "chicken", "broccoli", "healthy", "dairy"],
    },
    {
        "name": "Overnight Oats with Banana",
        "recipe": "Mix 80g oats, 200ml milk, 1 banana sliced, 1 tbsp honey. Refrigerate overnight. Top with berries.",
        "ingredients": "80g oats, 200ml milk, 1 banana, honey, berries",
        "tags": ["breakfast", "healthy", "budget", "vegetarian", "dairy", "gluten"],
    },
    {
        "name": "Lentil Vegetable Soup",
        "recipe": "Sauté onion, carrot, celery. Add 200g red lentils, 1L vegetable stock, cumin, paprika. Simmer 25 min.",
        "ingredients": "200g red lentils, 1 onion, 2 carrots, celery, vegetable stock, cumin, paprika",
        "tags": ["healthy", "budget", "vegetarian", "saving_money", "soup", "vegan"],
    },
    {
        "name": "Scrambled Eggs with Toast",
        "recipe": "Whisk 3 eggs with splash of milk, salt, pepper. Cook over low heat stirring constantly. Serve on 2 slices toasted bread.",
        "ingredients": "3 eggs, 2 slices bread, milk, butter, salt, pepper",
        "tags": ["breakfast", "budget", "quick", "saving_money", "eggs", "gluten", "dairy"],
    },
    {
        "name": "Grilled Salmon with Sweet Potato",
        "recipe": "Season 150g salmon fillet. Grill 4 min per side. Roast 200g sweet potato cubes at 200C for 25 min with olive oil.",
        "ingredients": "150g salmon fillet, 200g sweet potato, olive oil, lemon, garlic",
        "tags": ["healthy", "longevity", "fish", "protein", "salmon"],
    },
    {
        "name": "Greek Yogurt Parfait",
        "recipe": "Layer 200g Greek yogurt, 50g granola, mixed berries. Drizzle with honey.",
        "ingredients": "200g Greek yogurt, 50g granola, mixed berries, honey",
        "tags": ["breakfast", "snack", "healthy", "protein", "dairy", "gluten"],
    },
    {
        "name": "Avocado Toast with Poached Eggs",
        "recipe": "Toast 2 slices sourdough. Mash 1 avocado with lemon juice, salt. Top with 2 poached eggs and chilli flakes.",
        "ingredients": "2 slices sourdough, 1 avocado, 2 eggs, lemon, chilli flakes",
        "tags": ["breakfast", "healthy", "avocado", "eggs", "gluten"],
    },
    {
        "name": "Steak with Roasted Vegetables",
        "recipe": "Season 200g ribeye with salt, pepper, garlic. Sear 3 min per side. Rest 5 min. Roast mixed vegetables at 200C for 30 min.",
        "ingredients": "200g ribeye steak, mixed vegetables, garlic, olive oil, rosemary",
        "tags": ["protein", "bulking", "steak", "beef", "healthy"],
    },
]


def _searchable(recipe: dict) -> str:
    return (recipe["name"] + " " + recipe["ingredients"] + " " + " ".join(recipe["tags"])).lower()


def _affinity(recipe: str, likes: list[str], allergies: list[str]) -> str:
    """Compute a descriptive affinity label for a single recipe."""
    lower_allergies = [a.lower() for a in allergies]
    lower_likes = [l.lower() for l in likes]

    if any(allergen in recipe for allergen in lower_allergies):
        return "allergic"

    matched_likes = [like for like in lower_likes if like in recipe]
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

    Args:
        keywords: Search terms, e.g. ["protein", "bulking", "chicken"].
        likes: Foods the user enjoys, e.g. ["steak", "avocado"]. Used to
               set user_affinity to "loved" or "liked".
        allergies: Known allergens, e.g. ["gluten", "dairy"]. Recipes
                   containing these are marked "allergic" — the Meal
                   Planner should exclude them.

    Returns:
        List of recipe dicts ordered by relevance, each with an added
        "user_affinity" field: "loved" | "liked" | "neutral" | "allergic".
    """
    _likes = likes or []
    _allergies = allergies or []
    lower_kw = [k.lower() for k in keywords]

    scored = []
    for r in RECIPES:
        searchable = _searchable(r)
        kw_score = sum(1 for kw in lower_kw if kw in searchable)
        if not lower_kw or kw_score > 0:
            recipe_with_affinity = dict(r)
            recipe_with_affinity["user_affinity"] = _affinity(searchable, _likes, _allergies)
            scored.append((kw_score, recipe_with_affinity))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = [r for _, r in scored]

    if not results:
        fallback = []
        for r in RECIPES[:3]:
            recipe_with_affinity = dict(r)
            recipe_with_affinity["user_affinity"] = _affinity(_searchable(r), _likes, _allergies)
            fallback.append(recipe_with_affinity)
        return fallback

    return results
