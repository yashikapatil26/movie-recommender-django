from __future__ import annotations

import os
from functools import lru_cache
from urllib.parse import quote_plus

import requests

DEFAULT_POSTER = (
    "https://images.unsplash.com/photo-1594909122845-11baa439b7bf"
    "?q=80&w=300&h=450&auto=format&fit=crop"
)


def _get_api_key() -> str:
    """Return OMDb API key.
    """

    return os.getenv("OMDB_API_KEY", "")


@lru_cache(maxsize=2048)
def fetch_movie_details(movie_title: str) -> dict[str, str]:
    """Fetch poster + metadata from OMDb.

    Cached in-process to reduce repeat OMDb calls.
    """

    title = (movie_title or "").strip()
    if not title:
        return {
            "title": "",
            "poster": DEFAULT_POSTER,
            "rating": "N/A",
            "year": "Unknown",
            "genre": "Movie",
        }

    api_key = _get_api_key()
    if not api_key:
        return {
            "title": title,
            "poster": DEFAULT_POSTER,
            "rating": "N/A",
            "year": "Unknown",
            "genre": "Movie",
        }

    url = f"https://www.omdbapi.com/?t={quote_plus(title)}&apikey={api_key}"

    data: dict[str, str] = {}
    try:
        response = requests.get(url, timeout=5)
        if response.ok:
            data = response.json() or {}
    except Exception:
        data = {}

    poster = data.get("Poster") or DEFAULT_POSTER
    if poster == "N/A":
        poster = DEFAULT_POSTER

    genre_raw = data.get("Genre") or "Movie"
    genre = (genre_raw.split(",")[0].strip() if genre_raw else "Movie") or "Movie"

    return {
        "title": title,
        "poster": poster,
        "rating": data.get("imdbRating") or "N/A",
        "year": data.get("Year") or "Unknown",
        "genre": genre,
    }


def clear_omdb_cache() -> None:
    fetch_movie_details.cache_clear()
