"""
image_populator.py

Walks a generated itinerary dict and fills in every empty image["url"]
field with a real photo URL from the Pexels API, using image["alt"]
(plus optional context like destination name) as the search query.

Requires: pip install requests --break-system-packages
Set PEXELS_API_KEY in your environment or .env file.

Get a free key at: https://www.pexels.com/api/
Free tier: 200 requests/hour, 20,000 requests/month - comfortable for
iterating and running full itineraries without much throttling worry.
"""

import os
import time
import requests
from functools import lru_cache

PEXELS_API_URL = "https://api.pexels.com/v1/search"
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# Simple in-process cache so identical queries within one run don't
# burn extra API calls (e.g. "Wayanad temple" appearing twice).
@lru_cache(maxsize=256)
def _search_pexels(query: str, orientation: str = "landscape"):
    if not PEXELS_API_KEY:
        raise RuntimeError(
            "PEXELS_API_KEY is not set. Get a free key at "
            "https://www.pexels.com/api/ and set it in your .env"
        )

    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "query": query,
        "per_page": 1,
        "orientation": orientation,
    }

    resp = requests.get(PEXELS_API_URL, headers=headers, params=params, timeout=10)

    if resp.status_code == 429:
        raise RuntimeError("Pexels API rate limit hit.")
    if resp.status_code == 401:
        raise RuntimeError("Pexels API key invalid or missing.")
    resp.raise_for_status()

    photos = resp.json().get("photos", [])
    if not photos:
        return None

    photo = photos[0]
    return {
        "url": photo["src"]["large"],
        "url_small": photo["src"]["medium"],
        "photographer": photo["photographer"],
        "photographer_url": photo["photographer_url"],
        "pexels_url": photo["url"],
    }


def _build_query(alt_text: str, destination: str | None = None) -> str:
    """
    Build a focused search query. Pexels search works best with 2-4
    concrete keywords rather than a full descriptive sentence, so we
    trim the alt text down and optionally append the destination for
    better geographic relevance.
    """
    # Keep it short — take the first ~6 words of alt text
    words = alt_text.strip().split()
    trimmed = " ".join(words[:6])

    if destination:
        # Use just the primary place name (before any comma) to avoid
        # over-qualifying the query, e.g. "Wayanad, Kerala, India" -> "Wayanad"
        primary_place = destination.split(",")[0].strip()
        return f"{trimmed} {primary_place}"

    return trimmed


def populate_images(
    data: dict,
    destination: str | None = None,
    rate_limit_delay: float = 0.15,
    attribution: bool = True,
) -> dict:
    """
    Recursively walk `data` and fill in any dict matching the shape
    {"url": "", "alt": "..."} with a real Pexels image.

    Args:
        data: the itinerary dict (from result.model_dump())
        destination: optional destination string to sharpen search queries
        rate_limit_delay: seconds to sleep between API calls (be polite)
        attribution: if True, adds "photographer" and "photographer_url"
                      keys to each populated image dict (Pexels requires
                      visible attribution per their API guidelines)

    Returns:
        the same dict, mutated in place, also returned for convenience
    """
    if not PEXELS_API_KEY:
        raise RuntimeError(
            "PEXELS_API_KEY is not set. Get a free key at "
            "https://www.pexels.com/api/ and set it in your .env"
        )

    def _walk(node):
        if isinstance(node, dict):
            # Detect an image-shaped dict: has "url" and "alt" keys
            if "url" in node and "alt" in node and node.get("url", "") == "":
                query = _build_query(node.get("alt", ""), destination)
                if query:
                    try:
                        result = _search_pexels(query)
                    except Exception as e:
                        print(f"[image_populator] Warning: search failed for '{query}': {e}")
                        result = None

                    if result:
                        node["url"] = result["url"]
                        if attribution:
                            node["photographer"] = result["photographer"]
                            node["photographer_url"] = result["photographer_url"]
                    else:
                        # Fall back to a generic destination-only query once
                        # before giving up, so we at least get *something*.
                        if destination:
                            fallback_query = destination.split(",")[0].strip()
                            try:
                                fallback = _search_pexels(fallback_query)
                            except Exception:
                                fallback = None
                            if fallback:
                                node["url"] = fallback["url"]
                                if attribution:
                                    node["photographer"] = fallback["photographer"]
                                    node["photographer_url"] = fallback["photographer_url"]

                    time.sleep(rate_limit_delay)
            else:
                for value in node.values():
                    _walk(value)
        elif isinstance(node, list):
            for item in node:
                _walk(item)

    _walk(data)
    return data