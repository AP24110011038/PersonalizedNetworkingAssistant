"""
Fact-Checking Service
=======================
Uses the public Wikipedia REST API (no API key required) to fetch a short,
reliable summary for a search query. Two calls are used:
  1. `opensearch` action - resolves a loose user query (e.g. "blockchain in
     healthcare") to the closest matching article title.
  2. `page/summary/{title}` REST endpoint - returns a clean summary extract
     plus the canonical article URL.

This two-step approach handles imprecise user queries better than hitting
the summary endpoint directly with raw user text.
"""
from typing import Optional, Tuple
import logging
import requests

logger = logging.getLogger(__name__)

OPENSEARCH_URL = "https://en.wikipedia.org/w/api.php"
SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
REQUEST_TIMEOUT = 6  # seconds


class FactChecker:
    """Wraps Wikipedia's public API for quick fact verification."""

    def _resolve_title(self, query: str) -> Optional[str]:
        params = {
            "action": "opensearch",
            "search": query,
            "limit": 1,
            "namespace": 0,
            "format": "json",
        }
        response = requests.get(OPENSEARCH_URL, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        # opensearch returns [query, [titles], [descriptions], [urls]]
        titles = data[1] if len(data) > 1 else []
        return titles[0] if titles else None

    def _fetch_summary(self, title: str) -> Tuple[str, str]:
        response = requests.get(SUMMARY_URL.format(title=title.replace(" ", "_")), timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        summary = data.get("extract", "")
        url = data.get("content_urls", {}).get("desktop", {}).get("page", "")
        return summary, url

    def check_fact(self, query: str) -> dict:
        """
        Look up `query` on Wikipedia and return a dict with a short summary,
        the source URL, and whether a match was found. Never raises: on any
        failure (network issue, no results) it returns found=False with a
        helpful message.
        """
        try:
            title = self._resolve_title(query)
            if not title:
                return {
                    "query": query,
                    "summary": "No reliable Wikipedia reference was found for this query.",
                    "source_url": None,
                    "found": False,
                }

            summary, url = self._fetch_summary(title)
            if not summary:
                return {
                    "query": query,
                    "summary": "A matching article was found but no summary was available.",
                    "source_url": url or None,
                    "found": False,
                }

            return {
                "query": query,
                "summary": summary,
                "source_url": url,
                "found": True,
            }

        except requests.RequestException as exc:
            logger.warning("Wikipedia lookup failed for '%s': %s", query, exc)
            return {
                "query": query,
                "summary": "Fact-check service is temporarily unavailable. Please try again later.",
                "source_url": None,
                "found": False,
            }


# Module-level singleton
fact_checker = FactChecker()
