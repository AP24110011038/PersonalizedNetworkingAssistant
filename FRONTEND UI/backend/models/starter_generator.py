"""
Conversation Starter Generation Service
=========================================
Model Research & Selection notes:
- GPT-2 (small, 124M params) was chosen over larger generative models
  because it runs comfortably on CPU, has no API cost, and is "good
  enough" for short, templated conversation-starter generation once
  properly prompted. Larger models (GPT-2 medium/large, GPT-J, etc.)
  were considered but rejected for this use case due to latency and
  memory footprint in a lightweight demo app.
- We use prompt engineering (few-shot style prompt) rather than
  fine-tuning, since fine-tuning GPT-2 would require a labeled dataset
  of "good" conversation starters that doesn't exist yet. This is
  called out in the README as a future improvement once user feedback
  (thumbs up/down) accumulates enough data to build one.
- Post-processing trims/deduplicates GPT-2's raw output into 2-3 clean
  starters, since raw generation is noisy and can run on past the
  intended sentence.
"""
from typing import List
import logging
import re

logger = logging.getLogger(__name__)


class StarterGenerator:
    """Wraps a GPT-2 text-generation pipeline for conversation starters."""

    def __init__(self, model_name: str = "gpt2"):
        self.model_name = model_name
        self._pipeline = None  # lazy-loaded

    def _load_pipeline(self):
        if self._pipeline is None:
            from transformers import pipeline
            logger.info("Loading starter generation model: %s", self.model_name)
            self._pipeline = pipeline("text-generation", model=self.model_name)
        return self._pipeline

    def _build_prompt(self, themes: List[str], interests: List[str]) -> str:
        theme_str = ", ".join(themes) if themes else "networking"
        interest_str = ", ".join(interests) if interests else "meeting new people"
        return (
            f"Event themes: {theme_str}. Attendee interests: {interest_str}.\n"
            f"Write a friendly, specific conversation starter to open a chat "
            f"with someone at this event:\n1."
        )

    def generate_starters(self, themes: List[str], interests: List[str] = None, num_starters: int = 3) -> List[str]:
        """
        Generate `num_starters` conversation starters tailored to the given
        themes and user interests. Falls back to a template-based generator
        if the GPT-2 pipeline can't be loaded, so the app stays usable
        without internet access / cached model weights.
        """
        interests = interests or []
        prompt = self._build_prompt(themes, interests)

        try:
            generator = self._load_pipeline()
            outputs = generator(
                prompt,
                max_new_tokens=60,
                num_return_sequences=num_starters,
                do_sample=True,
                top_p=0.92,
                temperature=0.9,
                pad_token_id=50256,  # gpt2 eos token id, silences padding warnings
            )
            starters = [self._clean_output(o["generated_text"], prompt) for o in outputs]
            starters = [s for s in starters if s]
            if not starters:
                raise ValueError("No usable starters generated")
            return starters[:num_starters]

        except Exception as exc:  # pragma: no cover - exercised via fallback tests
            logger.warning("Falling back to template-based starters: %s", exc)
            return self._fallback_templates(themes, interests, num_starters)

    @staticmethod
    def _clean_output(generated_text: str, prompt: str) -> str:
        """Strip the prompt echo and trim to the first full sentence(s)."""
        text = generated_text.replace(prompt, "").strip()
        # Cut off anything after a newline (GPT-2 tends to keep rambling)
        text = text.split("\n")[0].strip()
        # Ensure it ends on sentence punctuation
        match = re.search(r"^(.*?[.!?])", text)
        if match:
            text = match.group(1)
        return text.strip(" -1.")

    @staticmethod
    def _fallback_templates(themes: List[str], interests: List[str], num_starters: int) -> List[str]:
        theme_str = themes[0] if themes else "this event"
        interest_str = interests[0] if interests else "the topics here"
        templates = [
            f"I noticed this event focuses on {theme_str} — what got you interested in {interest_str}?",
            f"What's your take on how {theme_str} is shaping {interest_str} these days?",
            f"I'm curious what brought you to a session on {theme_str} — are you working in that space?",
        ]
        return templates[:num_starters]


# Module-level singleton so the model is loaded once per process
starter_generator = StarterGenerator()
