"""Shared Pydantic models for inter-agent data contracts.

Each sub-agent declares output_schema=<Model> so ADK enforces structured
output, and output_key=<key> so the result is saved to session state
automatically. The orchestrator reads from state rather than parsing
free-text from the context window.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Meal Planner output
# ---------------------------------------------------------------------------

class DayPlan(BaseModel):
    day: int = Field(description="Day number, e.g. 1 for Monday")
    breakfast: str | None = Field(None, description="Breakfast meal name and brief description")
    lunch: str | None = Field(None, description="Lunch meal name and brief description")
    dinner: str | None = Field(None, description="Dinner meal name and brief description")
    snacks: str | None = Field(None, description="Snack(s) for the day")


class MealPlan(BaseModel):
    days: list[DayPlan] = Field(description="Ordered list of daily meal plans")


# ---------------------------------------------------------------------------
# Ingredient Aggregator output
# ---------------------------------------------------------------------------

class ShoppingItem(BaseModel):
    ingredient: str = Field(description="Ingredient name, e.g. 'chicken breast'")
    quantity: str = Field(description="Amount to buy, e.g. '1kg', '6 eggs', '2 x 500g pack'")


class ShoppingList(BaseModel):
    shopping_list: list[ShoppingItem] = Field(description="Complete list of ingredients to buy")


# ---------------------------------------------------------------------------
# Store Finder output
# ---------------------------------------------------------------------------

class Store(BaseModel):
    name: str = Field(description="Store name, e.g. 'Albert'")
    address: str = Field(description="Full store address string")
    distance_km: float = Field(description="Distance from user address in kilometres")


class StoreList(BaseModel):
    stores: list[Store] = Field(description="Nearby stores sorted by distance ascending")


# ---------------------------------------------------------------------------
# Store Buyer output
# ---------------------------------------------------------------------------

class PricedItem(BaseModel):
    ingredient: str = Field(description="Ingredient name from the shopping list")
    product: str = Field(description="Exact product name as found in the store")
    price_eur: float = Field(description="Price in EUR for the chosen product")


class StoreTotal(BaseModel):
    name: str = Field(description="Store name")
    address: str = Field(description="Store address")
    total_eur: float = Field(description="Sum of cheapest available products for all ingredients")


class PriceResult(BaseModel):
    cheapest_store: StoreTotal = Field(description="Store with the lowest total cost")
    items: list[PricedItem] = Field(description="Line items for the cheapest store")
    all_stores: list[StoreTotal] = Field(description="All stores ranked by total cost ascending")
