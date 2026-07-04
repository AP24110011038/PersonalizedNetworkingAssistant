"""
Integration tests for the FastAPI routes using TestClient.

Model calls (theme extraction, starter generation, Wikipedia lookups) are
mocked so the whole test suite runs quickly and fully offline.
"""
from unittest.mock import patch
from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@patch("backend.routes.starters.starter_generator")
@patch("backend.routes.starters.theme_extractor")
def test_generate_starters_endpoint(mock_theme_extractor, mock_starter_generator, tmp_path, monkeypatch):
    from backend.services import history_service
    fake_file = tmp_path / "history.json"
    fake_file.write_text("[]")
    monkeypatch.setattr(history_service, "DATA_FILE", fake_file)
    monkeypatch.setattr(history_service, "DATA_DIR", tmp_path)

    mock_theme_extractor.extract_themes.return_value = ["AI", "sustainability"]
    mock_starter_generator.generate_starters.return_value = [
        "What excites you about AI in cities?",
        "How did you get into sustainability work?",
    ]

    resp = client.post("/starters/generate", json={
        "event_description": "AI for Sustainable Cities",
        "interests": ["climate change", "urban planning"],
        "user_id": "alice",
    })

    assert resp.status_code == 200
    data = resp.json()
    assert data["themes"] == ["AI", "sustainability"]
    assert len(data["starters"]) == 2
    assert "history_id" in data


@patch("backend.routes.factcheck.fact_checker")
def test_factcheck_endpoint(mock_fact_checker):
    mock_fact_checker.check_fact.return_value = {
        "query": "blockchain in healthcare",
        "summary": "Blockchain is a distributed ledger technology used in healthcare data systems.",
        "source_url": "https://en.wikipedia.org/wiki/Blockchain",
        "found": True,
    }

    resp = client.post("/factcheck/query", json={"query": "blockchain in healthcare"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["found"] is True
    assert "distributed ledger" in data["summary"]


def test_history_endpoint_empty(tmp_path, monkeypatch):
    from backend.services import history_service
    fake_file = tmp_path / "history.json"
    fake_file.write_text("[]")
    monkeypatch.setattr(history_service, "DATA_FILE", fake_file)
    monkeypatch.setattr(history_service, "DATA_DIR", tmp_path)

    resp = client.get("/history/", params={"user_id": "nobody"})
    assert resp.status_code == 200
    assert resp.json() == []


def test_feedback_endpoint_not_found(tmp_path, monkeypatch):
    from backend.services import history_service
    fake_file = tmp_path / "history.json"
    fake_file.write_text("[]")
    monkeypatch.setattr(history_service, "DATA_FILE", fake_file)
    monkeypatch.setattr(history_service, "DATA_DIR", tmp_path)

    resp = client.post("/history/feedback", json={"history_id": "does-not-exist", "useful": True})
    assert resp.status_code == 404
