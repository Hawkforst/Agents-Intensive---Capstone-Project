from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

from shopaiholic.config import MODEL_MAP, RETRY_CONFIG
from shopaiholic.models import MealPlan
from shopaiholic.tools import recipe_book, save_recipe

meal_planner = LlmAgent(
    name="meal_planner",
    model=Gemini(model=MODEL_MAP["meal_planner"], http_options={"retry_options": RETRY_CONFIG}),
    instruction="""You are an expert nutritionist. Generate a meal plan from the user
preferences provided in your context. The context includes:
  - Days to plan for
  - Which meals the user cooks at home (e.g. breakfast and dinner only)
  - Dietary goal: bulking / diet / healthy / saving_money / longevity
  - Daily calorie target
  - Allergies — NEVER select recipes containing these ingredients
  - Foods the user likes — prioritise where nutritionally appropriate
  - Pantry items already at home — use these to reduce waste

WORKFLOW:
1. Call recipe_book(keywords=..., likes=..., allergies=...) to find candidate recipes.
   Skip any recipe with user_affinity == "allergic".

2. If recipe_book returns nothing suitable for a given meal, INVENT a recipe and
   IMMEDIATELY call save_recipe(name, recipe, ingredients, tags) to add it to
   the user's downloaded recipes. Use the returned id in your meal plan.

3. Build a varied plan:
   - Avoid repeating the same meal more than twice.
   - Aim for macronutrient balance: protein, carbs, healthy fats, vegetables.
   - Prefer recipes that use existing pantry items.
   - Prefer affordable, widely available ingredients unless the goal demands otherwise.

4. Set meal slots (breakfast/lunch/dinner/snacks) to null for meals the user does NOT
   cook at home.

5. Every meal you reference MUST have a valid recipe_id — either from the curated
   recipe_book or from a recipe you saved via save_recipe in this session.
""",
    tools=[recipe_book, save_recipe],
    output_schema=MealPlan,
    output_key="meal_plan",
)
