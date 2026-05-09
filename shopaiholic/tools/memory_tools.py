"""user_preferences and food_storage tools backed by LocalMemoryStore."""

from __future__ import annotations

from typing import Any

from google.adk.tools.tool_context import ToolContext

from shopaiholic.memory import memory_store


def _user_id(tool_context: ToolContext | None) -> str:
    if tool_context and tool_context.user_id:
        return tool_context.user_id
    return "default_user"


def user_preferences(
    action: str,
    days: int | None = None,
    meals: list[str] | None = None,
    goal: str | None = None,
    maintenance_calories: int | None = None,
    allergies: list[str] | None = None,
    likes: list[str] | None = None,
    address_street: str | None = None,
    address_city: str | None = None,
    address_zip: str | None = None,
    address_country: str | None = None,
    max_distance: float | None = None,
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Retrieve or save permanent user shopping and dietary preferences.

    Args:
        action: "retrieve" to read preferences, "save" to write them.
        days: Number of days to plan shopping for (e.g. 7).
        meals: Meals the user cooks at home, e.g. ["breakfast", "dinner"].
        goal: Dietary goal — one of "bulking", "diet", "healthy", "saving_money".
        maintenance_calories: Daily calorie target (integer).
        allergies: List of allergens, e.g. ["peanuts", "gluten"].
        likes: Foods the user enjoys, e.g. ["steak", "avocado"].
        address_street: Street and number, e.g. "Main St 123".
        address_city: City name.
        address_zip: Postal/ZIP code.
        address_country: Country name.
        max_distance: Max distance in km to search for stores.
        tool_context: Injected by ADK — do not pass manually.

    Returns:
        On "retrieve": full preferences dict.
        On "save": {"status": "saved", "preferences": {...}}.
    """
    uid = _user_id(tool_context)

    if action == "retrieve":
        return memory_store.get_prefs(uid)

    if action == "save":
        updates: dict[str, Any] = {}
        if days is not None:
            updates["days"] = days
        if meals is not None:
            updates["meals"] = meals
        if goal is not None:
            updates["goal"] = goal
        if maintenance_calories is not None:
            updates["maintenance_calories"] = maintenance_calories
        if allergies is not None:
            updates["allergies"] = allergies
        if likes is not None:
            updates["likes"] = likes
        if max_distance is not None:
            updates["max_distance"] = max_distance

        address_parts = {
            k: v
            for k, v in {
                "street": address_street,
                "city": address_city,
                "zip": address_zip,
                "country": address_country,
            }.items()
            if v is not None
        }
        if address_parts:
            existing = memory_store.get_prefs(uid).get("address", {})
            existing.update(address_parts)
            updates["address"] = existing

        saved = memory_store.set_prefs(uid, updates)
        return {"status": "saved", "preferences": saved}

    return {"error": f"Unknown action '{action}'. Use 'retrieve' or 'save'."}


def food_storage(
    action: str,
    item: str = "",
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """Retrieve or update the user's food pantry.

    Args:
        action: "retrieve" to list all items, "add" to add an item,
                "remove" to remove an item.
        item: Item string for "add"/"remove", e.g. "500g chicken breast".
        tool_context: Injected by ADK — do not pass manually.

    Returns:
        retrieve: {"pantry": ["500g chicken", "2l milk", ...]}
        add/remove: {"status": "added"/"removed", "pantry": [...]}
    """
    uid = _user_id(tool_context)

    if action == "retrieve":
        return {"pantry": memory_store.get_pantry(uid)}

    if action == "add":
        if not item:
            return {"error": "Provide an 'item' string to add."}
        pantry = memory_store.add_pantry(uid, item)
        return {"status": "added", "pantry": pantry}

    if action == "remove":
        if not item:
            return {"error": "Provide an 'item' string to remove."}
        pantry = memory_store.remove_pantry(uid, item)
        return {"status": "removed", "pantry": pantry}

    return {"error": f"Unknown action '{action}'. Use 'retrieve', 'add', or 'remove'."}
