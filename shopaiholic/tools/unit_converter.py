"""Unit converter tool for the Ingredient Aggregator.

Converts between common cooking units so the aggregator can sum
ingredients expressed in different units (e.g. 500g + 1kg = 1500g).
Supports weight (g/kg/oz/lb) and volume (ml/l/cup/tbsp/tsp).
"""

from __future__ import annotations

_WEIGHT_TO_G: dict[str, float] = {
    "g": 1.0,
    "gram": 1.0,
    "grams": 1.0,
    "kg": 1000.0,
    "kilogram": 1000.0,
    "kilograms": 1000.0,
    "oz": 28.3495,
    "ounce": 28.3495,
    "ounces": 28.3495,
    "lb": 453.592,
    "lbs": 453.592,
    "pound": 453.592,
    "pounds": 453.592,
}

_VOLUME_TO_ML: dict[str, float] = {
    "ml": 1.0,
    "milliliter": 1.0,
    "milliliters": 1.0,
    "millilitre": 1.0,
    "millilitres": 1.0,
    "l": 1000.0,
    "liter": 1000.0,
    "liters": 1000.0,
    "litre": 1000.0,
    "litres": 1000.0,
    "cup": 240.0,
    "cups": 240.0,
    "tbsp": 15.0,
    "tablespoon": 15.0,
    "tablespoons": 15.0,
    "tsp": 5.0,
    "teaspoon": 5.0,
    "teaspoons": 5.0,
    "fl oz": 29.5735,
    "fluid ounce": 29.5735,
    "fluid ounces": 29.5735,
}


def convert_unit(value: float, from_unit: str, to_unit: str) -> dict:
    """Convert a quantity from one unit to another.

    Supports weight units (g, kg, oz, lb) and volume units
    (ml, l, cup, tbsp, tsp). Cannot convert between weight and volume.

    Args:
        value: Numeric amount to convert, e.g. 500.
        from_unit: Source unit string, e.g. "g", "kg", "cup".
        to_unit: Target unit string, e.g. "kg", "ml", "l".

    Returns:
        Dict with "result" (float, rounded to 3 dp) and "unit" (str),
        or "error" (str) if the conversion is not supported.

    Examples:
        convert_unit(500, "g", "kg")  -> {"result": 0.5, "unit": "kg"}
        convert_unit(2, "cup", "ml") -> {"result": 480.0, "unit": "ml"}
    """
    f = from_unit.lower().strip()
    t = to_unit.lower().strip()

    if f in _WEIGHT_TO_G and t in _WEIGHT_TO_G:
        result = value * _WEIGHT_TO_G[f] / _WEIGHT_TO_G[t]
        return {"result": round(result, 3), "unit": to_unit}

    if f in _VOLUME_TO_ML and t in _VOLUME_TO_ML:
        result = value * _VOLUME_TO_ML[f] / _VOLUME_TO_ML[t]
        return {"result": round(result, 3), "unit": to_unit}

    if (f in _WEIGHT_TO_G and t in _VOLUME_TO_ML) or (
        f in _VOLUME_TO_ML and t in _WEIGHT_TO_G
    ):
        return {"error": "Cannot convert between weight and volume units."}

    return {"error": f"Unknown unit(s): '{from_unit}' or '{to_unit}'."}
