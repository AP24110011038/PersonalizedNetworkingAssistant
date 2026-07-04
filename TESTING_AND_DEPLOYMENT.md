# Testing Philosophy and Local Deployment

## Testing Philosophy and Framework Selection

The project uses `pytest` as the main testing framework because it is simple, readable, and well suited for testing FastAPI services. The test suite focuses on the most important application behavior:

- Theme extraction from event descriptions
- Conversation starter generation
- Wikipedia fact-checking response handling
- FastAPI route behavior using `TestClient`

The testing approach separates service testing from API testing. Service tests check individual business logic modules, while API route tests verify that the backend endpoints accept requests and return correct responses.

## Testing the Event Analyzer Service

File: `tests/test_event_analyzer.py`

This test verifies that the event analyzer can extract useful themes from the sample event description.

```python
from app.services.event_analyzer import EventAnalyzerService


def test_extract_themes_from_event_description():
    analyzer = EventAnalyzerService()

    themes = analyzer.extract_themes(
        "AI for Sustainable Cities",
        ["climate change", "urban planning"],
    )

    assert "AI" in themes
    assert "sustainability" in themes
    assert "climate change" in themes
```

Expected result:

- The service identifies `AI`.
- The service identifies `sustainability`.
- The service includes user interests such as `climate change`.

## Testing the Topic Generator Service

File: `tests/test_topic_generator.py`

This test checks that the topic generator creates three useful conversation prompts.

```python
from app.services.topic_generator import TopicGeneratorService


def test_generate_starters_returns_three_prompts():
    generator = TopicGeneratorService()

    starters = generator.generate_starters(
        event_description="AI for Sustainable Cities",
        themes=["AI", "sustainability"],
        interests=["climate change", "urban planning"],
        user_goal="meet collaborators",
    )

    assert len(starters) == 3
    assert all(len(starter) > 20 for starter in starters)
```

Expected result:

- The generator returns exactly three starters.
- Each starter is long enough to be meaningful.
- The generated prompts are connected to the event theme and user interests.

## Testing the Fact Checker Service

File: `tests/test_fact_checker.py`

The fact checker uses the Wikipedia API. To avoid depending on live internet access during testing, the test uses a mocked response.

```python
from app.services.fact_checker import FactCheckerService


class FakeResponse:
    status_code = 200

    def raise_for_status(self):
        return None

    def json(self):
        return {
            "title": "Blockchain",
            "extract": "A blockchain is a distributed ledger.",
            "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Blockchain"}},
        }


def test_fact_checker_uses_wikipedia_summary(monkeypatch):
    def fake_get(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr("app.services.fact_checker.requests.get", fake_get)
    service = FactCheckerService()

    result = service.fact_check("blockchain")

    assert result["title"] == "Blockchain"
    assert "distributed ledger" in result["summary"]
    assert result["source"] == "Wikipedia"
```

Expected result:

- The service correctly reads the Wikipedia title.
- The service returns a summary.
- The source is shown as Wikipedia.

## Testing API Routes with httpx TestClient

File: `tests/test_api_routes.py`

FastAPI's `TestClient` is based on HTTPX, so it allows API endpoints to be tested without starting a real server.

The route tests cover:

- `GET /health`
- `POST /generate`
- `POST /feedback`

Example route test:

```python
def test_health_check():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

The generate route test uses temporary JSON files so test data does not affect real application history.

Expected result:

- API health check returns status `ok`.
- Generate endpoint returns conversation starters and themes.
- Feedback endpoint saves thumbs up/down feedback.

## Running Tests and Interpreting Results

Install dependencies:

```bash
pip install -r requirements.txt
```

Run all tests:

```bash
pytest
```

Run a single test file:

```bash
pytest tests/test_event_analyzer.py
```

Expected successful output:

```text
tests/test_event_analyzer.py .
tests/test_topic_generator.py .
tests/test_fact_checker.py .
tests/test_api_routes.py ...

passed
```

If a test fails:

- Read the failing test name.
- Check the assertion message.
- Compare the expected output with the actual output.
- Fix the related service or route file.
- Run `pytest` again.

## Local Deployment

Start the FastAPI backend:

```bash
uvicorn app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

FastAPI automatic documentation:

```text
http://127.0.0.1:8000/docs
```

Start the Streamlit frontend in a second terminal:

```bash
streamlit run frontend/streamlit_app.py
```

Frontend URL:

```text
http://localhost:8501
```

## Manual Testing and Verification

### Scenario 1: Generating Smart Starters

Input:

```text
Event description: AI for Sustainable Cities
Interests: climate change, urban planning
Goal: meet collaborators
```

Expected output:

- Extracted themes such as `AI`, `sustainability`, and `climate change`
- Three conversation starters
- Generated result saved in conversation history

### Scenario 2: Quick Fact Verification

Input:

```text
blockchain in healthcare
```

Expected output:

- Wikipedia-based title
- Short summary
- Reference link

### Scenario 3: Reviewing Past Strategies

Steps:

1. Generate conversation starters.
2. Mark at least one suggestion as useful.
3. Open the History tab.
4. Open the Feedback tab.

Expected output:

- History tab shows previous generated conversations.
- Feedback tab shows whether starters were marked useful or not useful.

## Conclusion

The project uses a clear and modular testing strategy. Unit tests verify each service independently, API tests verify backend routes, and manual testing confirms that the full FastAPI and Streamlit workflow works correctly from the user's perspective.
