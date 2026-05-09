"""Local JSON-backed memory store.

Replaces VertexAiMemoryBankService for offline/local runs. The on-disk shape is:

    {
        "<user_id>": {
            "prefs": {...},
            "pantry": [...]
        },
        ...
    }

The store keeps a per-user dict so multiple users can share one file. Reads
load lazily, writes flush immediately so a session crash doesn't lose data.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

DEFAULT_PATH = Path.home() / ".shopaiholic" / "memory.json"

_DEFAULT_PREFS: dict[str, Any] = {
    "days": 7,
    "meals": ["breakfast", "lunch", "dinner"],
    "goal": "healthy",
    "maintenance_calories": 2500,
    "allergies": [],
    "likes": [],
    "address": {},
    "max_distance": 10,
}


class LocalMemoryStore:
    def __init__(self, path: Path | str = DEFAULT_PATH) -> None:
        self.path = Path(path)
        self._lock = threading.Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("{}", encoding="utf-8")

    def _load(self) -> dict[str, Any]:
        with self.path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def _save(self, data: dict[str, Any]) -> None:
        tmp = self.path.with_suffix(".json.tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        tmp.replace(self.path)

    def get_prefs(self, user_id: str) -> dict[str, Any]:
        with self._lock:
            data = self._load()
        prefs = dict(_DEFAULT_PREFS)
        prefs.update(data.get(user_id, {}).get("prefs", {}))
        return prefs

    def set_prefs(self, user_id: str, prefs: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            data = self._load()
            user = data.setdefault(user_id, {})
            current = dict(_DEFAULT_PREFS)
            current.update(user.get("prefs", {}))
            current.update(prefs)
            user["prefs"] = current
            self._save(data)
            return current

    def get_pantry(self, user_id: str) -> list[dict[str, Any]]:
        """Returns list of {name, quantity, unit} dicts."""
        with self._lock:
            data = self._load()
        return list(data.get(user_id, {}).get("pantry", []))

    def add_pantry(self, user_id: str, name: str, quantity: float, unit: str) -> list[dict]:
        """Add or top up a pantry item. If the same (name, unit) already
        exists, the quantity is summed instead of duplicating the entry."""
        with self._lock:
            data = self._load()
            user = data.setdefault(user_id, {})
            pantry: list[dict] = user.setdefault("pantry", [])
            for entry in pantry:
                if entry["name"] == name and entry["unit"] == unit:
                    entry["quantity"] = float(entry["quantity"]) + float(quantity)
                    break
            else:
                pantry.append({"name": name, "quantity": float(quantity), "unit": unit})
            self._save(data)
            return list(pantry)

    def remove_pantry(self, user_id: str, name: str) -> list[dict]:
        """Remove all entries for the given ingredient name."""
        with self._lock:
            data = self._load()
            user = data.setdefault(user_id, {})
            pantry: list[dict] = user.setdefault("pantry", [])
            user["pantry"] = [e for e in pantry if e["name"] != name]
            self._save(data)
            return list(user["pantry"])


memory_store = LocalMemoryStore()
