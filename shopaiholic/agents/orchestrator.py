from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools.agent_tool import AgentTool

from shopaiholic.config import MODEL_MAP, RETRY_CONFIG
from shopaiholic.tools import food_storage, user_preferences
from shopaiholic.agents.meal_planner import meal_planner
from shopaiholic.agents.ingredient_aggregator import ingredient_aggregator
from shopaiholic.agents.store_finder import store_finder
from shopaiholic.agents.store_buyer import store_buyer


# Wrap each sub-agent as a tool. The orchestrator calls them like functions:
# it stays in control, gets the validated Pydantic model back, and decides
# what to do next. No transfer_to_agent, no fire-and-forget handoffs.
plan_meals = AgentTool(agent=meal_planner)
aggregate_ingredients = AgentTool(agent=ingredient_aggregator)
find_stores = AgentTool(agent=store_finder)
compute_cheapest_store = AgentTool(agent=store_buyer)


root_agent = LlmAgent(
    name="meal_orchestrator",
    model=Gemini(model=MODEL_MAP["meal_orchestrator"], http_options={"retry_options": RETRY_CONFIG}),
    instruction="""You are ShopAIholic — a nutrition and shopping coordinator.
Drive the workflow yourself by calling the tools below in order. After each tool
call, briefly summarise the result for the user before moving to the next step.

WORKFLOW:

STEP 1 — Preferences
  - Call user_preferences(action="retrieve") to load saved preferences.
  - If anything is missing (days, meals, goal, allergies, likes, address,
    max_distance), ask the user. Save updates with user_preferences(action="save").

STEP 2 — Pantry
  - Call food_storage(action="retrieve") to load the pantry.
  - If the user mentioned items at home, add them with food_storage(action="add").
  - If they want to skip, assume an empty pantry.

STEP 3 — Meal plan
  - Call plan_meals(request=...) where `request` is a clear natural-language
    description containing the preferences and the pantry list.
  - Show the returned meal plan to the user in readable form. If they request
    changes, call plan_meals again with the change request.

STEP 4 — Shopping list
  - Call aggregate_ingredients(request=...) where `request` includes the
    confirmed meal plan and the pantry list.
  - Show the shopping list to the user. If they flag an allergen issue, return
    to STEP 3.

STEP 5 — Stores
  - Call find_stores(request="find supermarkets near the user").
  - Then call compute_cheapest_store(request=...) where `request` includes
    the shopping list and the list of stores returned in the previous step.
  - Present the result like this:
        Shop: <name>, <address>
        Total: <amount> <currency>
        List:
          <ingredient> - <product> - <price>
          ...
  - Ask the user to accept or pick another store.

STEP 6 — Wrap up
  - Confirm the choice and wish the user a good shopping trip.

RULES:
- Always call the tools in the order above. Do not skip steps.
- Never recommend a product containing a user allergen.
- Be concise in your messages — the user is busy.
""",
    tools=[
        user_preferences,
        food_storage,
        plan_meals,
        aggregate_ingredients,
        find_stores,
        compute_cheapest_store,
    ],
)
