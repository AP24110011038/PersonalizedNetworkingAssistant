"""
Unit tests for FactChecker.

All network calls to Wikipedia are mocked so tests run offline and
deterministically.
"""
from unittest.mock import patch, MagicMock
from backend.models.fact_checker import FactChecker


def _mock_response(json_data, status_ok=True):
    mock_resp = MagicMock()
    mock_resp.json.return_value = json_data
    mock_resp.raise_for_status = MagicMock() if status_ok else MagicMock(side_effect=Exception("HTTP error"))
    return mock_resp


@patch("backend.models.fact_checker.requests.get")
def test_check_fact_success(mock_get):
    opensearch_response = _mock_response(["blockchain in healthcare", ["Blockchain"], [], []])
    summary_response = _mock_response({
        "extract": "Blockchain is a distributed ledger technology.",
        "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Blockchain"}},
    })
    mock_get.side_effect = [opensearch_response, summary_response]

    checker = FactChecker()
    result = checker.check_fact("blockchain in healthcare")

    assert result["found"] is True
    assert "distributed ledger" in result["summary"]
    assert result["source_url"] == "https://en.wikipedia.org/wiki/Blockchain"


@patch("backend.models.fact_checker.requests.get")
def test_check_fact_no_results(mock_get):
    opensearch_response = _mock_response(["asdkjaskldj", [], [], []])
    mock_get.side_effect = [opensearch_response]

    checker = FactChecker()
    result = checker.check_fact("asdkjaskldj")

    assert result["found"] is False
    assert result["source_url"] is None


@patch("backend.models.fact_checker.requests.get")
def test_check_fact_network_failure(mock_get):
    import requests
    mock_get.side_effect = requests.RequestException("network down")

    checker = FactChecker()
    result = checker.check_fact("blockchain")

    assert result["found"] is False
    assert "unavailable" in result["summary"].lower()
