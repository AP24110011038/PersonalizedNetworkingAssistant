# Project Topics and File Mapping

## Epic: Pre-requisites

- Install Python dependencies from `requirements.txt`.
- Run FastAPI backend with `uvicorn app.main:app --reload`.
- Run Streamlit frontend with `streamlit run frontend/streamlit_app.py`.

## Epic: Project Flow

1. User enters event description, interests, and goal in Streamlit.
2. Streamlit sends the request to FastAPI.
3. Event Analyzer extracts themes.
4. Topic Generator creates conversation starters.
5. History Logger stores generated results.
6. User submits thumbs up/down feedback.
7. Feedback Logger stores personalization feedback.

## Epic 1: Model Selection and Architecture

- DistilBERT-ready theme extraction: `app/services/event_analyzer.py`
- GPT-2-ready conversation generation: `app/services/topic_generator.py`
- Modular backend architecture: `app/main.py`, `app/api/routes.py`, `app/services/`

The code supports Hugging Face `transformers` models when installed. If model packages are not available, fallback logic keeps the app usable for demos and tests.

## Epic 2: Core Functionalities Development

- Data Schema Definition: `app/models/schemas.py`
- Event Analyzer Service: `app/services/event_analyzer.py`
- Topic Generator Service: `app/services/topic_generator.py`
- Fact Checker Service: `app/services/fact_checker.py`
- History Logger Service: `app/services/history_logger.py`
- Feedback Logger Service: `app/services/feedback_logger.py`
- API Routes: `app/api/routes.py`
- Application Entry Point: `app/main.py`

## Epic 3: Main Application Logic

- Centralized routing is handled in `app/api/routes.py`.
- Service layer design keeps business logic separate from HTTP routes.
- FastAPI features used:
  - Pydantic request and response models
  - Dependency injection
  - Automatic API documentation
  - CORS middleware
  - Typed route responses

## Epic 4: Frontend UI Using Streamlit

All frontend features are implemented in `frontend/streamlit_app.py`.

- Application setup and configuration
- Input section and generation flow
- Results display and feedback buttons
- Fact-checking section
- Conversation history view
- Feedback history view
- Streamlit session state for recent generated results

## Epic 5: Testing and Local Deployment

- Testing framework: pytest
- Event analyzer tests: `tests/test_event_analyzer.py`
- Topic generator tests: `tests/test_topic_generator.py`
- Fact checker tests: `tests/test_fact_checker.py`
- API route tests: `tests/test_api_routes.py`
- Local deployment instructions: `README.md`

## Scenario Coverage

### Scenario 1: Generating Smart Starters

Endpoint: `POST /generate`

Example input:

```json
{
  "event_description": "AI for Sustainable Cities",
  "interests": ["climate change", "urban planning"],
  "user_goal": "meet collaborators"
}
```

### Scenario 2: Quick Fact Verification

Endpoint: `POST /fact-check`

Example input:

```json
{
  "query": "blockchain in healthcare"
}
```

### Scenario 3: Reviewing Past Strategies

Endpoints:

- `GET /history`
- `POST /feedback`
- `GET /feedback`
