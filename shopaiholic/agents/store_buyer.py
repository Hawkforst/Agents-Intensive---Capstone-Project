from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

from shopaiholic.config import MODEL_MAP, RETRY_CONFIG
from shopaiholic.tools import supermarket_api_tools

store_buyer = LlmAgent(
    name="store_buyer",
    model=Gemini(model=MODEL_MAP["store_buyer"], http_options={"retry_options": RETRY_CONFIG}),
    instruction="""You are a price comparison agent. You receive a shopping list and a list of
nearby stores in your context. Your job is to find the cheapest store to buy everything.

Steps:
1. For each store in the store list, and for each ingredient in the shopping list:
   a. Call supermarket_api_tools(address=store_address, food_item=ingredient_name).
   b. From the returned items, select the option with the lowest price that covers
      the required quantity (prefer larger packs when they are cheaper per unit).
   c. Record: store, ingredient, chosen product name, price.
2. Sum the total cost per store across all ingredients.
3. Identify the store with the lowest total.
4. If an ingredient is unavailable at a store (empty items list), mark it as "not available"
   and exclude that store from being recommended as cheapest.

Output format — strict JSON, no extra text:
{
  "cheapest_store": {
    "name": "Albert",
    "address": "Happyville 21 Albert",
    "total_eur": 34.50,
    "items": [
      {"ingredient": "chicken breast", "product": "Fresh Chicken Breast 500g", "price_eur": 8.90},
      {"ingredient": "broccoli",       "product": "Broccoli 250g",             "price_eur": 2.90}
    ]
  },
  "all_stores": [
    {"name": "Albert", "address": "Happyville 21 Albert", "total_eur": 34.50},
    {"name": "Billa",  "address": "Happyville 113 Billa", "total_eur": 37.20}
  ]
}
""",
    tools=[supermarket_api_tools],
)
