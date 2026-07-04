# Personalized Networking Assistant

An AI-powered assistant that generates tailored conversation starters for
professional/social networking events, fact-checks topics via Wikipedia,
and lets users track which suggestions actually worked.

---

## 1. Model Research & Selection

| Task | Model chosen | Why |
|---|---|---|
| Theme extraction | `distilbert-base-nli-stsb-mean-tokens` (DistilBERT via `sentence-transformers`) | DistilBERT is ~40% smaller and ~60% faster than BERT with ~97% of its language understanding, which matters for a responsive app. The NLI/STSB-tuned variant produces embeddings well-suited to semantic similarity, so we embed the event description and a bank of candidate themes and rank by cosine similarity — no fine-tuning or labeled dataset required to get started. |
| Conversation starter generation | `gpt2` (small, 124M params) | Runs on CPU with no API cost, which fits a lightweight demo/prototype. Larger models (GPT-2 medium/large, GPT-Neo) were considered but rejected here due to latency/memory; the architecture allows swapping the model name with no other code changes. Quality is achieved primarily through prompt engineering rather than fine-tuning. |
| Fact verification | Wikipedia REST API (`opensearch` + `page/summary`) | Free, no API key, high-trust source for quick reference checks. No custom model needed — this is a retrieval task, not a generation task. |

**Alternatives considered and rejected:**
- *BERT-base* for theme extraction — more accurate in some benchmarks but ~2x slower/larger; not justified for short event-description inputs.
- *GPT-3.5/GPT-4 via API* for starter generation — better quality but introduces API cost/key management and an external dependency, which conflicts with the goal of a self-contained, testable app.
- *Custom fine-tuned generator* — rejected for v1 because there isn't yet a labeled dataset of "good" conversation starters. The thumbs-up/down feedback loop (Scenario 3) is designed specifically to collect this data over time, enabling a future fine-tuning pass.

**Graceful degradation:** both ML modules (`theme_extractor.py`, `starter_generator.py`) fall back to deterministic keyword/template logic if the model can't be loaded (e.g., no internet access to download weights). This keeps the app usable in constrained environments and makes unit testing possible without downloading multi-hundred-MB model files.

---

## 2. Application Architecture

```
personalized-networking-assistant/
├── backend/
│   ├── app.py                  # FastAPI entry point, mounts routers + CORS
│   ├── schemas.py               # Pydantic request/response models
│   ├── models/                  # ML/service wrappers (lazy-loaded)
│   │   ├── theme_extractor.py   # DistilBERT sentence embeddings + similarity
│   │   ├── starter_generator.py # GPT-2 text generation + post-processing
│   │   └── fact_checker.py      # Wikipedia REST API client
│   ├── services/
│   │   └── history_service.py   # JSON-file-backed conversation history/feedback
│   └── routes/
│       ├── starters.py          # POST /starters/generate      (Scenario 1)
│       ├── factcheck.py         # POST /factcheck/query        (Scenario 2)
│       └── history.py           # GET /history/, POST /history/feedback (Scenario 3)
├── frontend/
│   └── streamlit_app.py         # 3-tab UI calling the FastAPI backend over HTTP
├── tests/                       # pytest unit + integration tests (fully mocked, offline)
├── data/
│   └── history.json             # created at runtime; conversation history store
├── requirements.txt
└── README.md
```

**Design principles:**
- **Separation of concerns** — routes only orchestrate; all ML/business logic lives in `models/` and `services/`, making each piece independently unit-testable.
- **Lazy model loading** — models are loaded on first use (module-level singletons), not at import time, so importing the app for tests doesn't require downloading weights.
- **Fail-soft ML calls** — every model wrapper catches exceptions and falls back to a deterministic alternative, so a flaky/missing model never crashes the API.
- **Thin frontend** — Streamlit only handles presentation and calls the FastAPI backend over HTTP (`requests`), so the backend can also be used standalone (e.g., from a mobile client or Postman) without touching the UI.
- **File-based storage for v1** — `history_service.py` isolates all persistence behind a small function API (`add_entry`, `get_history`, `set_feedback`), so swapping the JSON file for SQLite/Postgres later is a localized change.

**Request flow (Scenario 1 example):**
```
Streamlit UI --POST /starters/generate--> FastAPI route
   -> theme_extractor.extract_themes()   (DistilBERT embeddings)
   -> starter_generator.generate_starters() (GPT-2 + prompt)
   -> history_service.add_entry()        (logs the result)
   <- StarterResponse (themes, starters, history_id)
```

---

## 3. Environment Setup

### Prerequisites
- Python 3.10+
- ~2 GB free disk space (for GPT-2 + DistilBERT model weights, downloaded on first run)
- Internet access on first run (to download model weights); afterward the app can run offline using cached weights, or fall back to template/keyword logic if weights aren't available.

### Setup steps

```bash
# 1. Clone/unzip the project, then move into it
cd personalized-networking-assistant

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the backend (FastAPI)
uvicorn backend.app:app --reload --port 8000
#    -> API docs available at http://localhost:8000/docs

# 5. In a second terminal, run the frontend (Streamlit)
source venv/bin/activate
streamlit run frontend/streamlit_app.py
#    -> UI available at http://localhost:8501

# 6. Run the test suite
pytest -v
```

### Environment variables (optional)
| Variable | Default | Purpose |
|---|---|---|
| `BACKEND_URL` | `http://localhost:8000` | Set this if the Streamlit frontend needs to reach a backend running on a different host/port. |

### Notes
- The first request to `/starters/generate` will trigger a one-time download of the DistilBERT and GPT-2 model weights (a few hundred MB total). Subsequent calls use the local Hugging Face cache (`~/.cache/huggingface`).
- If no internet access is available, both ML modules automatically fall back to deterministic keyword-matching / template-based logic — the app remains functional, just less "smart."
- `data/history.json` is created automatically on first use; delete it to reset history.

---

## Scenario Coverage Summary

| Scenario | Endpoint | Frontend tab |
|---|---|---|
| 1. Generating Smart Starters | `POST /starters/generate` | "✨ Generate Starters" |
| 2. Quick Fact Verification | `POST /factcheck/query` | "🔍 Fact Check" |
| 3. Reviewing Past Strategies | `GET /history/`, `POST /history/feedback` | "🕘 History" |
