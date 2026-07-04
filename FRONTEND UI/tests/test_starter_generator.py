"""
Unit tests for StarterGenerator.

We mock the GPT-2 pipeline so tests are fast and run without internet
access or downloading model weights, and separately test the fallback
template path used when the model can't be loaded.
"""
from backend.models.starter_generator import StarterGenerator


def test_clean_output_strips_prompt_and_trims_to_sentence():
    prompt = "Event themes: AI.\nWrite a starter:\n1."
    raw = prompt + " What do you think about AI's role in cities? Extra rambling text here"
    cleaned = StarterGenerator._clean_output(raw, prompt)
    assert cleaned.startswith("What do you think about AI's role in cities?")
    assert "Extra rambling" not in cleaned


def test_fallback_templates_returns_requested_count():
    generator = StarterGenerator()
    starters = generator._fallback_templates(["climate change"], ["urban planning"], num_starters=2)
    assert len(starters) == 2
    assert all(isinstance(s, str) and s for s in starters)


def test_generate_starters_uses_fallback_when_model_unavailable(monkeypatch):
    generator = StarterGenerator()

    def broken_loader():
        raise RuntimeError("no internet access / weights not cached")

    monkeypatch.setattr(generator, "_load_pipeline", broken_loader)
    starters = generator.generate_starters(["AI", "sustainability"], interests=["climate change"], num_starters=3)

    assert isinstance(starters, list)
    assert len(starters) == 3
    assert all(isinstance(s, str) and s for s in starters)


def test_generate_starters_with_mocked_pipeline(monkeypatch):
    generator = StarterGenerator()

    class FakePipeline:
        def __call__(self, prompt, **kwargs):
            n = kwargs.get("num_return_sequences", 1)
            return [{"generated_text": prompt + f" Mock starter number {i}."} for i in range(n)]

    monkeypatch.setattr(generator, "_load_pipeline", lambda: FakePipeline())
    starters = generator.generate_starters(["AI"], interests=["climate change"], num_starters=2)

    assert len(starters) == 2
    assert all("Mock starter number" in s for s in starters)
