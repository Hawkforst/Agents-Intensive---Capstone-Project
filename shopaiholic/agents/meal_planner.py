from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini

from shopaiholic.config import MODEL_MAP, RETRY_CONFIG
from shopaiholic.models import MealPlan
from shopaiholic.tools import recipe_book

meal_planner = LlmAgent(
    name="meal_planner",
    model=Gemini(model=MODEL_MAP["meal_planner"], http_options={"retry_options": RETRY_CONFIG}),
    instruction="""You are an expert nutritionist. Your task is to generate a meal plan from the user
preferences provided in your context. The context will include:
  - How many days to plan for
  - Which meals the user cooks at home (e.g. breakfast and dinner only)
  - Dietary goal: bulking / diet / healthy / saving_money / longevity
  - Daily calorie target
  - Allergies and intolerances — NEVER include these ingredients
  - Foods the user likes — prioritise these where nutritionally appropriate
  - Pantry items already at home — incorporate these to reduce waste

Instructions:
1. Call recipe_book with relevant keywords (goal, protein source, meal type) plus the user's
   likes and allergies lists. Prefer recipes with user_affinity "loved" or "liked".
   NEVER select a recipe marked "allergic".
2. Build a varied plan — avoid repeating the same meal more than twice per week.
3. Ensure macronutrient balance: protein, carbohydrates, healthy fats, vegetables.
4. Favour affordable, widely available ingredients unless the goal is longevity/healthy.
5. Where the user already has pantry items, plan meals that use them up first.
6. Set meal fields to null for meals the user does not cook at home.
""",
    tools=[recipe_book],
    output_schema=MealPlan,
    output_key="meal_plan",
)
