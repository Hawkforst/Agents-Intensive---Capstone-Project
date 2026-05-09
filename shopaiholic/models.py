"""Shared Pydantic models for inter-agent data contracts.

Recipes, pantry items, and shopping list entries all share the same
Ingredient shape so the deterministic aggregator can sum, subtract,
and compare them with simple name normalisation.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Shared primitives
# ---------------------------------------------------------------------------

class Ingredient(BaseModel):
    name: str = Field(description="Canonical ingredient name, lowercase, singular, no modifiers (e.g. 'chicken breast', 'rice', 'broccoli').")
    quantity: float = Field(description="Numeric amount, e.g. 150.0")
    unit: str = Field(description="Unit string: g, kg, ml, l, or 'each' for countable items")


# ---------------------------------------------------------------------------
# Meal Planner output
# ---------------------------------------------------------------------------

class MealReference(BaseModel):
    """A single meal slot pointing to a known recipe.

    Empty values (name="" and recipe_id="") mean the user does not cook
    this slot. The aggregator skips entries with empty recipe_id.
    """
    name: str = Field(default="", description="Recipe display name, or empty string if the user does not cook this slot")
    recipe_id: str = Field(default="", description="ID of the recipe in recipe_book or downloaded_recipes, or empty string to skip this slot")


class DayPlan(BaseModel):
    day: int = Field(description="Day number, e.g. 1 for Monday")
    breakfast: MealReference = Field(default_factory=MealReference)
    lunch: MealReference = Field(default_factory=MealReference)
    dinner: MealReference = Field(default_factory=MealReference)
    snacks: MealReference = Field(default_factory=MealReference)


class MealPlan(BaseModel):
    days: list[DayPlan]


# ---------------------------------------------------------------------------
# Aggregator output (shopping list)
# ---------------------------------------------------------------------------

class ShoppingItem(BaseModel):
    ingredient: str = Field(description="Canonical ingredient name")
    quantity: float = Field(description="Target amount to buy (rounded up)")
    unit: str = Field(description="Unit string")


class ShoppingList(BaseModel):
    shopping_list: list[ShoppingItem]


# ---------------------------------------------------------------------------
# Store Finder output
# ---------------------------------------------------------------------------

class Store(BaseModel):
    name: str
    address: str
    distance_km: float


class StoreList(BaseModel):
    stores: list[Store]


# ---------------------------------------------------------------------------
# Cheapest-store result
# ---------------------------------------------------------------------------

class PricedItem(BaseModel):
    ingredient: str
    product: str
    price_eur: float


class StoreTotal(BaseModel):
    name: str
    address: str
    total_eur: float


class PriceResult(BaseModel):
    cheapest_store: StoreTotal
    items: list[PricedItem]
    all_stores: list[StoreTotal]
