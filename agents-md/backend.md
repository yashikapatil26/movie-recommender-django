## Backend Implementation Report

### Summary

- Refactored recommendation logic into a cached module so TF‑IDF is not recomputed per request.
- Added cached OMDb fetching with request hardening (HTTPS, timeout, URL encoding).
- Added backend-driven `error_message` for “no results” cases.
- Added unit tests and view tests; tests mock OMDb/network calls.
- Switched the dataset download to a stable ZIP source and regenerated `movies.csv` (~4.8k titles).
- Added an ML model step (TF-IDF + SVD + kNN) for recommendations.
- Added backend search results support with deterministic matching (substring + fuzzy fallback).
- Removed hardcoded OMDb API key and added .env loading via python-dotenv.
- Added offline recommender artifact build/load flow to keep fitting out of requests.

### Files Changed

- `movie_engine/recommender.py` (new)
- `movie_engine/omdb.py` (new)
- `movie_engine/views.py`
- `movie_engine/tests.py`
- `.gitignore` (new)
- `download_data.py`
- `movies.csv`
- `README.md`
- `movie_engine/management/commands/build_recommender.py`

### How To Verify

- Run server: `python manage.py runserver`
- Manual:
  - Load `/` and confirm “Trending Now” renders.
  - Search a known title (e.g., “Inception”) and confirm 4 recommendations appear.
  - Search a nonsense title and confirm a warning message appears.
- Build artifacts: `python manage.py build_recommender`
- Run tests: `python manage.py test`

### Tests Added/Updated

- Recommender unit tests with a tiny generated CSV (fast).
- Home view tests that patch `fetch_movie_details` to avoid network.
- View tests updated to include `search_results` in context when querying.
- Recommender tests now build and load artifacts from a tiny CSV.

### Perf Notes

- Before: TF‑IDF + cosine computed on every search request.
- After: TF‑IDF is built once per process per dataset path; repeat searches reuse cached state. Also, the home page “Trending Now” does not trigger TF‑IDF building (it only loads titles).

### Open Questions / Follow-ups

- Do we want to delete the accidental HTML `movies_raw.csv` + `movies_raw_files/` from the repo?
