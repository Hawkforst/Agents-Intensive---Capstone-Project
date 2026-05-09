from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

from shopaiholic.config import MODEL_MAP, RETRY_CONFIG
from shopaiholic.models import ShoppingList
from shopaiholic.tools import convert_unit, recipe_book

ingredient_aggregator = LlmAgent(
    name="ingredient_aggregator",
    model=Gemini(model=MODEL_MAP["ingredient_aggregator"], http_options={"retry_options": RETRY_CONFIG}),
    instruction="""You are a precise ingredient aggregator. You receive a meal plan JSON and a pantry
list (items already at home) in your context. Your job is to produce a consolidated shopping list.

Steps:
1. For each meal in the plan, call recipe_book with the meal name as a keyword to retrieve
   exact ingredient amounts. If recipe_book returns no match, estimate standard serving sizes.
2. Aggregate ingredient quantities across all meals. Use convert_unit to normalise units
   before summing (e.g. combine 500g and 1kg into 1500g, then output as 1.5kg).
3. Subtract any quantities already available in the pantry list provided in your context.
   If a pantry item fully covers a recipe need, omit it from the shopping list.
   If it partially covers the need, list only the shortfall.
4. Round final quantities to sensible supermarket pack sizes (e.g. 1.1kg → buy 1.5kg pack).
5. Remove any ingredient that appears in the user's allergy list (double-check from context).
""",
    tools=[recipe_book, convert_unit],
    output_schema=ShoppingList,
    output_key="shopping_list",
)
