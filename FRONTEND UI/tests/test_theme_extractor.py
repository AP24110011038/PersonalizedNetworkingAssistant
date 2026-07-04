"""
Unit tests for ThemeExtractor.

The embedding model isn't mocked to load (no internet/model weights needed
in CI); instead we test the fallback keyword-matching path directly, and
verify the public `extract_themes` API degrades gracefully when the model
fails to load.
"""
from backend.models.theme_extractor import ThemeExtractor, CANDIDATE_THEMES


def test_fallback_keyword_match_finds_known_theme():
    extractor = ThemeExtractor()
    themes = extractor._fallback_keyword_match("A talk about climate change and cities", top_n=3)
    assert "climate change" in themes


def test_fallback_keyword_match_returns_default_when_no_match():
    extractor = ThemeExtractor()
    themes = extractor._fallback_keyword_match("something totally unrelated xyz", top_n=2)
    assert len(themes) == 2
    assert all(t in CANDIDATE_THEMES for t in themes)


def test_extract_themes_uses_fallback_when_model_unavailable(monkeypatch):
    extractor = ThemeExtractor()

    def broken_loader():
        raise RuntimeError("no internet access / weights not cached")

    monkeypatch.setattr(extractor, "_load_model", broken_loader)
    themes = extractor.extract_themes("AI for Sustainable Cities", interests=["urban planning"], top_n=2)

    assert isinstance(themes, list)
    assert len(themes) == 2
    assert "urban planning" in themes or "artificial intelligence" in themes


def test_extract_themes_respects_top_n(monkeypatch):
    extractor = ThemeExtractor()
    monkeypatch.setattr(extractor, "_load_model", lambda: (_ for _ in ()).throw(RuntimeError("offline")))
    themes = extractor.extract_themes("blockchain in healthcare", top_n=1)
    assert len(themes) == 1
