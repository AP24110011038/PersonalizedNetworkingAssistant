"""
Unit tests for history_service. Uses a temp file (via monkeypatch) so tests
never touch the real data/history.json.
"""
import json
from backend.services import history_service


def test_add_and_get_history(tmp_path, monkeypatch):
    fake_file = tmp_path / "history.json"
    fake_file.write_text("[]")
    monkeypatch.setattr(history_service, "DATA_FILE", fake_file)
    monkeypatch.setattr(history_service, "DATA_DIR", tmp_path)

    entry = history_service.add_entry(
        user_id="alice",
        event_description="AI for Sustainable Cities",
        interests=["climate change"],
        themes=["AI", "sustainability"],
        starters=["What drew you to this event?"],
    )

    assert entry["user_id"] == "alice"
    assert "id" in entry

    history = history_service.get_history("alice")
    assert len(history) == 1
    assert history[0]["event_description"] == "AI for Sustainable Cities"


def test_set_feedback_updates_entry(tmp_path, monkeypatch):
    fake_file = tmp_path / "history.json"
    fake_file.write_text("[]")
    monkeypatch.setattr(history_service, "DATA_FILE", fake_file)
    monkeypatch.setattr(history_service, "DATA_DIR", tmp_path)

    entry = history_service.add_entry("bob", "Fintech Meetup", [], ["fintech"], ["Hi there!"])
    updated = history_service.set_feedback(entry["id"], True)

    assert updated["feedback"] is True

    history = history_service.get_history("bob")
    assert history[0]["feedback"] is True


def test_set_feedback_missing_entry_returns_none(tmp_path, monkeypatch):
    fake_file = tmp_path / "history.json"
    fake_file.write_text("[]")
    monkeypatch.setattr(history_service, "DATA_FILE", fake_file)
    monkeypatch.setattr(history_service, "DATA_DIR", tmp_path)

    result = history_service.set_feedback("nonexistent-id", True)
    assert result is None


def test_get_history_filters_by_user(tmp_path, monkeypatch):
    fake_file = tmp_path / "history.json"
    fake_file.write_text("[]")
    monkeypatch.setattr(history_service, "DATA_FILE", fake_file)
    monkeypatch.setattr(history_service, "DATA_DIR", tmp_path)

    history_service.add_entry("alice", "Event A", [], ["theme"], ["starter"])
    history_service.add_entry("bob", "Event B", [], ["theme"], ["starter"])

    alice_history = history_service.get_history("alice")
    assert len(alice_history) == 1
    assert alice_history[0]["event_description"] == "Event A"
