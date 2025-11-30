# Agents Intensive Course Capstone Project: ShopAIholic
This is a respository for my 5-Day AI Agents Intensive Course with Google 2025 final project submission.


Category 1: The Pitch (Problem, Solution, Value)

## Problem:

The need to buy, cook and eat food is one of the few things that connects all 8.2 billion people living on Earth. Many of these people - especially in EU and NA increasingly want to not only eat something but rather eat high quality, nutritious and balanced diet, while also navigating numerous supermarket offers, time-limited discounts and, ultimately, saving money.

That requires careful planning, which takes a lot of time many people do not have. This makes it a perfect use-case for an agentic system.



## Solution:

ShopAIholic is a multi-agent system that helps users create their shopping lists and finds the cheapest nearby supermarket to buy everything they need.

It does so by engaging directly with the user to discover - and remember - their dietary goals, such as saving as much money as possible, gaining lean muscle, increasing their longevity or simply eating tasty food. Furthermore, it keeps track of user's food storage and verifies with the user by providing them with a list of foods and quantities they're supposed to have at home and updating its persistent memory based on new information. This behaviour is fully optional and the user is asked if they'd like to engage with the food storage memory feature.

Once user's dietary goals are established, it uses its Meal Planner sub-agent to derive a meal plan that matches users' goals. An overview of this plan is first presented to the user and changes are made based on feedback (e.g. "I don't like broccoli", which results in removal of broccoli meals as well as addition of this preference into persistent memory). This sub-agent is equipped with a recipe book API tool and Google search, which allows it to select tasty meals, which also follow dietary trends (since Google search is included).

When the meal plan is accepted by the user, next sub-agent, the Ingredient Aggregator, is used. The purpose of this sub-agent is to evaluate the amounts of individual ingredients that the user needs to buy. It dos so by iterating through the meal plan, summing up ingredients needed and using the persistent memory to access user's storage information. This reduces waste and saves the user money. To precisely evaluate the amount of ingredients needed, this sub-agent has access to a recipe book API tool, Google search as well as food storage memory knowledge from the context. 

After that, another agent, Store Finder, takes over. This agent is rather simplistic and uses Map Tools to find supermarkets near user's address.

The last piece of the puzzle that remains is to take the generated list of ingredients and find the cheapest place to do the shopping. This is the purpose of our last sub-agent, the Store Buyer. For nearby shops, it attempts to look up the price lists using APIs and Google Search, in case the use of APIs fails. The prices for each shops are then aggregated and the lowest total is given to the user along with the shopping list in a format of (store name - store address - $total; (list) item name - item quantity - total item price). The user is asked whether they agree with this shop or they'd like to reiterate some steps (e.g. choose another shop).



## Value:

For every user at least one of (3) options or their combination:

A) Average of ±60 minutes weekly saved on meal planning. `
[this is in the case the user is already actively planning their meals]

B) Significantly improved diet due to reasoning-driven planning based on user's goals. Up to 8-10 years of health span added (estimation based on longevity studies)
[this is in the case the user had poorly organised and/or unbalanced diet, which this agentic solution improves]

C) Around 10-20% groceries cost reduction.
[not guaranteed as vegetables cost more than instant noodle diet but overall value is still improved, savings can be specified via user interaction]


# Architecture overview:

<img width="4699" height="2410" alt="image" src="https://github.com/user-attachments/assets/8e2a8782-1ef2-44b4-8011-0cdd388051c2" />

**Agents** :


| Agent    | Role | Type | Model|
| -------- | ------- |------- |------ |
| Root Agent  | Coordinates main workflow, talks to client| Agent | gemini-2.5-flash |
| Meal Planner | Designs meal plans, works as a nutritionist | Sub-agent | gemini-2.5-pro |
| Ingredient Aggregator    | Calculates individual ingredient amounts| Sub-agent |gemini-2.5-flash |
| Store Finder    | Finds nearby stores |Sub-agent| gemini-2.5-flash-lite |
| Store Buyer    | Finds out total cost in each nearby store |Sub-agent| gemini-2.5-flash |

**Tools** :

| Tool    | Purpose | Type | 
| -------- | ------- |------- |
| google_search  | Look up recipes and other relevant information online | Built-in |
| user_preferences | Read and write relevant user preferences into persistent memory | Custom - interfaces persistent memory | 
| food_storage    | Read and write food in user's pantry | Custom - interfaces persistnet memory |
| recipe_book    | Finds recipes based on keywords provided | Custom - interfaces a recipe database via API | 
| maps_toolset    | Finds stores near user's address | MCPToolset tool set |





# Flaws and future improvements
Due to time constraints, many features haven't been (fully) developed or are underdeveloped. This section's purpose is to keep a TO-DO list of these flaws and highlight that I'm aware of these issues but haven't had the time to address everything:
