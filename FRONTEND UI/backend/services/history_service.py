"""
History Service
=================
Persists generated conversation starters and user feedback so users can
review past strategies (Scenario 3) and so the app has a growing dataset
of thumbs-up/down signal for future personalization or fine-tuning work.

Storage: a simple JSON file on disk (data/history.json). This keeps the
project dependency-free (no database setup needed) while still surviving
process restarts. Swapping this for a real database (SQLite/Postgres) is
a drop-in replacement since callers only interact with this module's
public functions.
"""
from typing import List, Optional, Dict
from pathlib import Path
from datetime import datetime, timezone
import json
import uuid
import threading

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DATA_FILE = DATA_DIR / "history.json"

_lock = threading.Lock()


def _ensure_storage() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text(json.dumps([]))


def _read_all() -> List[Dict]:
    _ensure_storage()
    with _lock:
        return json.loads(DATA_FILE.read_text() or "[]")


def _write_all(entries: List[Dict]) -> None:
    _ensure_storage()
    with _lock:
        DATA_FILE.write_text(json.dumps(entries, indent=2))


def add_entry(user_id: str, event_description: str, interests: List[str],
              themes: List[str], starters: List[str]) -> Dict:
    """Log a newly generated set of conversation starters. Returns the stored entry."""
    entries = _read_all()
    entry = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "event_description": event_description,
        "interests": interests,
        "themes": themes,
        "starters": starters,
        "feedback": None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    entries.append(entry)
    _write_all(entries)
    return entry


def get_history(user_id: Optional[str] = None) -> List[Dict]:
    """Return history entries, most recent first, optionally filtered by user."""
    entries = _read_all()
    if user_id:
        entries = [e for e in entries if e["user_id"] == user_id]
    return list(reversed(entries))


def set_feedback(history_id: str, useful: bool) -> Optional[Dict]:
    """Mark a history entry as useful (thumbs up) or not (thumbs down)."""
    entries = _read_all()
    for entry in entries:
        if entry["id"] == history_id:
            entry["feedback"] = useful
            _write_all(entries)
            return entry
    return None
