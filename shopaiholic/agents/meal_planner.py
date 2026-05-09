from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

from shopaiholic.config import MODEL_MAP, RETRY_CONFIG
from shopaiholic.models import MealPlan

meal_planner = LlmAgent(
    name="meal_planner",
    model=Gemini(model=MODEL_MAP["meal_planner"], http_options={"retry_options": RETRY_CONFIG}),
    instruction="""You are an expert nutritionist. Your only job is to choose meals from
the candidate recipes provided in your context and emit a structured MealPlan.

You will receive:
  - User preferences: days to plan, meals cooked at home, dietary goal, calorie
    target, allergies, likes
  - Pantry items already at home (use these to reduce waste)
  - A pool of candidate recipes, each with id, name, ingredients, tags, and a
    user_affinity rating

INSTRUCTIONS:
1. NEVER select a recipe with user_affinity == "allergic".
2. Prefer recipes with user_affinity "loved" or "liked".
3. Build a varied plan — avoid repeating the same meal more than twice.
4. Aim for macronutrient balance: protein, carbs, healthy fats, vegetables.
5. Prefer recipes that use existing pantry items first.
6. For each day, fill ONLY the meal slots the user cooks at home. Leave other
   slots as the default empty MealReference (name="" and recipe_id="").
7. Every selected meal MUST reference a recipe_id from the candidate pool —
   never invent IDs.
""",
    output_schema=MealPlan,
    output_key="meal_plan",
)
