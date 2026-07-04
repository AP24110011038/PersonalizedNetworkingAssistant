"""
Theme Extraction Service
=========================
Model Research & Selection notes:
- We use `sentence-transformers/distilbert-base-nli-stsb-mean-tokens`
  (a DistilBERT backbone fine-tuned for sentence similarity) rather than
  vanilla DistilBERT, because raw DistilBERT embeddings are not optimized
  for semantic similarity out of the box. This gives us fast, lightweight
  sentence embeddings we can compare against a candidate theme list.
- Approach: embed the event description, embed a bank of candidate
  networking themes, and return the top-N themes by cosine similarity.
  This keeps inference cheap (DistilBERT is ~40% smaller/faster than BERT)
  which matters for a responsive Streamlit/FastAPI app.
- The candidate theme bank is intentionally editable so the assistant can
  be extended to new domains (tech, healthcare, finance, etc.) without
  retraining anything.
"""
from typing import List
import logging

logger = logging.getLogger(__name__)

# Candidate theme bank used for similarity matching. This can be extended
# or loaded from a config/DB in a production deployment.
CANDIDATE_THEMES = [
    "artificial intelligence", "machine learning", "sustainability",
    "climate change", "urban planning", "renewable energy",
    "blockchain", "healthcare innovation", "fintech", "cybersecurity",
    "startups", "venture capital", "product management", "data science",
    "cloud computing", "biotechnology", "education technology",
    "remote work", "diversity and inclusion", "leadership",
    "supply chain", "e-commerce", "digital marketing", "robotics",
    "smart cities", "circular economy", "public policy",
]


class ThemeExtractor:
    """Wraps a sentence-embedding model for lightweight theme extraction."""

    def __init__(self, model_name: str = "distilbert-base-nli-stsb-mean-tokens"):
        self.model_name = model_name
        self._model = None  # lazy-loaded so imports/tests don't require the model weights

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading theme extraction model: %s", self.model_name)
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def extract_themes(self, text: str, interests: List[str] = None, top_n: int = 3) -> List[str]:
        """
        Extract the top_n most relevant themes for a given event description,
        optionally boosted by the user's stated interests.

        Falls back to simple keyword overlap if the embedding model can't be
        loaded (e.g. no internet access / no weights cached), so the rest of
        the app keeps working in constrained environments.
        """
        interests = interests or []
        combined_text = f"{text}. Interests: {', '.join(interests)}" if interests else text

        try:
            model = self._load_model()
            from sentence_transformers import util

            text_embedding = model.encode(combined_text, convert_to_tensor=True)
            theme_embeddings = model.encode(CANDIDATE_THEMES, convert_to_tensor=True)
            scores = util.cos_sim(text_embedding, theme_embeddings)[0]

            ranked = sorted(
                zip(CANDIDATE_THEMES, scores.tolist()),
                key=lambda pair: pair[1],
                reverse=True,
            )
            return [theme for theme, _ in ranked[:top_n]]

        except Exception as exc:  # pragma: no cover - exercised via fallback tests
            logger.warning("Falling back to keyword matching for theme extraction: %s", exc)
            return self._fallback_keyword_match(combined_text, top_n)

    @staticmethod
    def _fallback_keyword_match(text: str, top_n: int) -> List[str]:
        """Simple, dependency-free fallback: substring match against the theme bank."""
        text_lower = text.lower()
        matches = [theme for theme in CANDIDATE_THEMES if theme in text_lower]
        if not matches:
            # last resort: return the first few generic themes
            matches = CANDIDATE_THEMES[:top_n]
        return matches[:top_n]


# Module-level singleton so the model is loaded once per process
theme_extractor = ThemeExtractor()
