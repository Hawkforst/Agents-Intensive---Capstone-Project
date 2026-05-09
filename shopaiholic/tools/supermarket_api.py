"""Mock supermarket API tool.

Simulates per-store price lookups. Replace MOCK_DATA with real API calls
per retailer when integrating production data.
"""

from __future__ import annotations

MOCK_DATA: dict[tuple[str, str], list[dict]] = {
    ("happyville 21 albert", "chicken"): [
        {"name": "Fresh Chicken Breast 500g", "price": 8.90, "unit": "EUR/pack"},
        {"name": "Organic Whole Chicken 1.2kg", "price": 10.90, "unit": "EUR/each"},
        {"name": "Chicken Thighs 1kg", "price": 12.90, "unit": "EUR/kg"},
    ],
    ("happyville 113 billa", "chicken"): [
        {"name": "Billa Chicken Breast Fillet 400g", "price": 9.90, "unit": "EUR/pack"},
        {"name": "Billa Chicken Drumsticks 800g", "price": 9.90, "unit": "EUR/pack"},
    ],
    ("happyville 21 albert", "broccoli"): [
        {"name": "Broccoli 250g", "price": 2.90, "unit": "EUR/pack"},
        {"name": "Organic Broccoli 300g", "price": 9.90, "unit": "EUR/pack"},
    ],
    ("happyville 113 billa", "broccoli"): [
        {"name": "Fresh Broccoli 300g", "price": 5.90, "unit": "EUR/pack"},
    ],
    ("happyville 21 albert", "beef"): [
        {"name": "Beef Sirloin 400g", "price": 12.90, "unit": "EUR/pack"},
        {"name": "Beef Mince 500g", "price": 7.90, "unit": "EUR/pack"},
    ],
    ("happyville 113 billa", "beef"): [
        {"name": "Billa Beef Mince 500g", "price": 7.50, "unit": "EUR/pack"},
        {"name": "Billa Beef Steak 300g", "price": 11.90, "unit": "EUR/pack"},
    ],
    ("happyville 21 albert", "eggs"): [
        {"name": "Free Range Eggs 10-pack", "price": 3.50, "unit": "EUR/pack"},
        {"name": "Organic Eggs 6-pack", "price": 2.90, "unit": "EUR/pack"},
    ],
    ("happyville 113 billa", "eggs"): [
        {"name": "Billa Eggs 10-pack", "price": 3.20, "unit": "EUR/pack"},
    ],
    ("happyville 21 albert", "milk"): [
        {"name": "Whole Milk 1l", "price": 1.20, "unit": "EUR/l"},
        {"name": "Semi-Skimmed Milk 1l", "price": 1.10, "unit": "EUR/l"},
    ],
    ("happyville 113 billa", "milk"): [
        {"name": "Billa Whole Milk 1l", "price": 1.15, "unit": "EUR/l"},
    ],
    ("happyville 21 albert", "rice"): [
        {"name": "Long Grain Rice 1kg", "price": 1.80, "unit": "EUR/kg"},
        {"name": "Basmati Rice 1kg", "price": 2.50, "unit": "EUR/kg"},
    ],
    ("happyville 113 billa", "rice"): [
        {"name": "Billa Rice 1kg", "price": 1.60, "unit": "EUR/kg"},
    ],
    ("happyville 21 albert", "oats"): [
        {"name": "Rolled Oats 500g", "price": 1.40, "unit": "EUR/pack"},
    ],
    ("happyville 113 billa", "oats"): [
        {"name": "Billa Oats 500g", "price": 1.30, "unit": "EUR/pack"},
    ],
    ("happyville 21 albert", "lentils"): [
        {"name": "Red Lentils 500g", "price": 1.90, "unit": "EUR/pack"},
    ],
    ("happyville 113 billa", "lentils"): [
        {"name": "Billa Red Lentils 500g", "price": 1.70, "unit": "EUR/pack"},
    ],
    ("happyville 21 albert", "salmon"): [
        {"name": "Atlantic Salmon Fillet 300g", "price": 8.90, "unit": "EUR/pack"},
    ],
    ("happyville 113 billa", "salmon"): [
        {"name": "Billa Salmon Fillet 250g", "price": 7.90, "unit": "EUR/pack"},
    ],
    ("happyville 21 albert", "steak"): [
        {"name": "Ribeye Steak 250g", "price": 14.90, "unit": "EUR/pack"},
        {"name": "Sirloin Steak 300g", "price": 12.90, "unit": "EUR/pack"},
    ],
    ("happyville 113 billa", "steak"): [
        {"name": "Billa Sirloin Steak 300g", "price": 11.90, "unit": "EUR/pack"},
    ],
    ("happyville 21 albert", "avocado"): [
        {"name": "Avocado 2-pack", "price": 2.50, "unit": "EUR/pack"},
    ],
    ("happyville 113 billa", "avocado"): [
        {"name": "Ripe Avocado each", "price": 1.20, "unit": "EUR/each"},
    ],
    ("happyville 21 albert", "yogurt"): [
        {"name": "Greek Yogurt 500g", "price": 2.20, "unit": "EUR/pack"},
    ],
    ("happyville 113 billa", "yogurt"): [
        {"name": "Billa Greek Yogurt 400g", "price": 1.90, "unit": "EUR/pack"},
    ],
}


def supermarket_api_tools(address: str, food_item: str) -> dict:
    """Look up available products and prices for a food item at a given store.

    Args:
        address: Store location string, e.g. "Happyville 21 Albert".
        food_item: Keyword to search for, e.g. "chicken", "broccoli", "steak".

    Returns:
        Dict with "store" (str) and "items" (list). Each item has:
          name (str), price (float), unit (str, e.g. "EUR/pack").
        Returns empty items list when the combination is not in the database.
    """
    key = (address.lower(), food_item.lower())
    items = MOCK_DATA.get(key, [])
    return {"store": address, "items": items}
