# Agents Intensive Course Capstone Project: ShopAIholic
This is a respository for my 5-Day AI Agents Intensive Course with Google 2025 final project submission.

ShopAIholic - a smart assistent that helps you plan your shopping the way YOU want it. Help you reach your goals and save money and time!
<img width="2327" height="733" alt="image" src="https://github.com/user-attachments/assets/e6ff3e3a-709f-4eb1-b41b-6cad4b010006" />


Category 1: The Pitch (Problem, Solution, Value)

## Problem:

The need to buy, cook and eat food is one of the few things that connects all 8.2 billion people living on Earth. Many of these people increasingly want to not only eat something but rather eat high quality, nutritious and balanced diet, while also navigating numerous supermarket offers, time-limited discounts and, ultimately, saving money.

That requires careful planning, which takes a lot of time many people do not have - and even if they do, could fill it with more enjoyable or productive endeavours. This makes it a perfect use-case for an agentic system.



## Solution:

ShopAIholic is a multi-agent system that helps users create their shopping lists and finds the cheapest nearby supermarket to buy everything they need.

It does so by engaging directly with the user to discover - and remember through multiple sessions - their dietary goals, such as saving as much money as possible, gaining lean muscle, increasing their longevity or simply eating tasty food. Furthermore, it keeps track of user's food storage to reduce waste.

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

<img width="4756" height="2410" alt="image" src="https://github.com/user-attachments/assets/79e9c0b8-b88e-4140-9a8e-c482bce40ff3" />

**Agents** :


| Agent    | Role | Type | Model| Reasoning|
| -------- | ------- |------- |------ |------ |
| Root Agent  | Coordinates main workflow, talks to client| Agent | gemini-2.5-flash | Fast response needed, needs to understand but no complex reasoning needed |
| Meal Planner | Designs meal plans, works as a nutritionist | Sub-agent | gemini-2.5-pro | Deeper reasoning required to create high quality meal plans |
| Ingredient Aggregator    | Calculates individual ingredient amounts| Sub-agent |gemini-2.5-flash | Only basic reasoning needed to aggregate ingredients from recipes |
| Store Finder    | Finds nearby stores |Sub-agent| gemini-2.5-flash-lite | Only an API-called, no big reasoning capacity needed. |
| Store Buyer    | Finds out total cost in each nearby store |Sub-agent| gemini-2.5-flash | Basic mathematics needed and tool use needed. |

**Tools** :

| Tool    | Purpose | Type | 
| -------- | ------- |------- |
| google_search  | Look up recipes and other relevant information online | Built-in |
| user_preferences | Read and write relevant user preferences into persistent memory | Custom - interfaces persistent memory | 
| food_storage    | Read and write food in user's pantry | Custom - interfaces persistnet memory |
| recipe_book    | Finds recipes based on keywords provided | Custom - interfaces a recipe database via API | 
| supermarket_api_tools | Interfaces APIs for different shops to streamline their use by (sub)agents | Custom - interfaces shop APIs | 
| maps_toolset    | Finds stores near user's address | MCPToolset tool set |

**Plugins** :

| Plugin    | Purpose | 
| -------- | ------- |
| ReflectAndRetryToolPlugin  | Use this built-in plugin to handle, reflec-upon and hopefully fix issues


# Architecture: an overview of my design reasoning

I have opted for an architecture relying on one orchestrator agent and 4 sub-agents equipped with a number of tools. 

1. The root agent - Meal Orchestrator:
The Meal Orchestrator is responsible for communicating with the client and orchestrating general flow. It should first figure out what the user wants - this is done by direct communication and via persistent memory tools, which serve to retrieve user dietary preferences and needs, as well as their food storage at home. 
After that, it orchestrates the workflow given in its instructions. I opted for somewhat restrictive instructions with points based workflow to prevent the Agent getting sidetracked or not using individual sub-agents for their intended tasks. 
Due to the orchestration nature of this agent, it does not have to be as powerful as the Meal Planner  agent, which does more complex reasoning. Hence, faster and less expensive agent size can be used. (although this would need to be calibrated and tested in a production deployment scenario).
The Meal Orchestrator is also equipped with the ReflectAndRetryToolPlugin plugin with the aim to add robustness to the agentic system.

2. First sub-agent - Meal Planner:
This agent does the heavy-lifting in terms of reasoning. It works with the context built up by the Meal Orchestrator and its interaction with the user. This is also the reason I opted for the sub-agent type for this agent, rather than Agent-as-tool one. It's tasked with taking user preferences and goals (e.g. bulking, 3500 kcal maintenance, loves chicken, cooks only breakfast and dinner) into a meal plan. For this task, it has been equipped with a Recipe book tool (which is just a mock tool in this submission due to time constraints) and is tasked to find recipes there. This aims to provide coherence and quality to the meals offered. it is also tasked to suggest recipes where the user already has some ingredients at home. Furthermore, Google Search tool is also added to enhance its capabilities to provide good quality meals as well as adapt to specific needs where the Recipe Book might not suffice. 

3. Second sub-agent - Ingredient Aggregator:
The Ingredient Aggregator is a somewhat simpler agent where the design decision to make it a sub-agent, as opposed to agent-as-a-tool, is slightly more questionable. Nevertheless, I opted for the sub-agent architecture as context might be important in some instances, e.g. the user is following a gluten-free diet, and similar edge-cases might be difficult to handle using only agent-as-a-tool.  It is further tasked with subtracting ingredients the user already has at home.
Its role is to take the meal plan and convert it into a list of individual ingredients. It is again equipped with several tools to help it stay coherent and accurate. 

4. Third sub-agent - Store Finder
This is the smallest sub-agent. Its task is to use map APIs to search for stores near user's address. I opted for a smaller, cheaper model to use for this sub-agent. Other valid solutions might be to convert it into an agent-as-a-tool or write a tool that other agents call - likely to be used by the Store Buyer sub-agent. 

5. Fourth sub-agent - Store Buyer
The Store Buyer is a sub-agent that takes the ingredient list within the agent context (note: this might be a design flaw and it might be better for the Ingredient Aggregator to save the ingredient list into the InMemorySessionService to enhance robustness) as well as the list of nearest stores (again, InMemorySessionService would likely be more robust). It is equipped with a Store APIs tool, as well as Google Search, which helps it retrieve prices of individual ingredient items at nearby stores. It is tasked with aggregating the ingredient list and calculating total prices. 

6. Meal Orchestrator Output
The Meal Orchestrator gives the user a shopping list, the name of the cheapest nearby store and the total price. The user is then allowed to respond, possibly rejecting or asking the agent to re-do certain parts of the process.



# Flaws and future improvements
Due to time constraints, many features haven't been (fully) developed or are underdeveloped. This section's purpose is to keep a TO-DO list of these flaws and highlight that I'm aware of these issues but haven't had the time to address everything:


* Persistent memory: better design and implementation. Currently it's more of a mock implementation and I'm too time constrained to make meaningful progress before the submission.
* addition and subtraction of ingredients code for pantry, rather than simple setting, needs to be added for it to work properly
* The Store Finder sub-agent should possibly be converted into an Agent-as-a-tool or even just a tool.
