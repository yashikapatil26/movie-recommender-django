## Backend Task List (Owner: Backend Agent)

**Goal**: Keep the current SSR UX exactly as-is, but make recommendations fast, reduce OMDb calls, and make dataset handling/repo hygiene reliable.

**Roadmap Choice (College Project)**:

- Security: remove any hardcoded/default OMDb API keys; load from environment (optionally via `.env`).
- ML pipeline: move TF‑IDF/SVD/kNN “fitting” out of the request path by precomputing artifacts on disk.

**New Feature Goal**: After searching, render shelves in this order:

1. Smart picks for "<query>" (existing)
2. Search results for "<query>" (new)
3. Trending Now (existing)

### P0 — Correctness & Repo Hygiene

- [x] Add root `.gitignore` to avoid committing local artifacts.
- [ ] Decide what to do with `movies_raw.csv` (currently HTML) and `movies_raw_files/` (recommended: delete from repo; `.gitignore` already ignores them).
- [ ] Align dataset reality with project goal:
  - Option A: Keep the small demo `movies.csv` and update README to say “demo dataset”.
  - Option B: Regenerate + commit a ~5k cleaned `movies.csv` using `download_data.py`.

### P1 — Performance (Stop TF‑IDF Recompute Per Request)

- [x] Move recommendation logic into a cached module.
- [x] Avoid building full NxN cosine matrix; compute similarity from one row.
- [x] Guard edge cases (empty dataset, too few rows).

### P1 — OMDb Robustness + Caching

- [x] Add in-process cache for OMDb responses.
- [x] Harden OMDb requests (URL-encode title, HTTPS, timeout, safe defaults).

### P0 — Security (OMDb API Key)

- [ ] Remove any hardcoded/default OMDb API key from source.
- [ ] Require `OMDB_API_KEY` via environment variable for OMDb lookups.
- [ ] (Recommended) Add `.env` support for local dev using `python-dotenv`:
  - Add dependency.
  - Load `.env` early (e.g., in `manage.py` / `mysite/settings.py`).
  - Ensure `.env` is in `.gitignore`.
- [ ] Update README to document configuration (no keys in code, how to set `OMDB_API_KEY`).
- [ ] Add a safe fallback behavior if `OMDB_API_KEY` is missing (e.g., skip network call and return placeholder poster/metadata).

### P2 — Search Behavior + User Feedback

- [x] Normalize user query (trim whitespace).
- [x] Add `error_message` in context when no match is found (no `print()` debugging).

### P0 — Search Results Shelf (New)

- [x] Add backend support for a separate `search_results` list (cards) for the current query.
- [x] Define a deterministic title matching strategy against `movies.csv` (keep it simple):
  - Case-insensitive substring match on `title`.
  - If zero substring hits, fall back to a small fuzzy match list (e.g., best N titles).
  - Cap results (e.g., 8–12) to avoid excessive OMDb calls.
- [x] Populate `search_results` with the same card fields used elsewhere (title, poster, rating/year/genre if available) using the existing OMDb fetch + cache.
- [x] Ensure the view always provides `search_results` in the template context (empty list when no query or no matches).
- [ ] (Optional) De-duplicate titles across `recommendations` and `search_results` for cleaner UX.

### P1 — ML Pipeline (Precompute Artifacts)

- [ ] Create an offline build step (script or management command), e.g. `python manage.py build_recommender`:
  - Load `movies.csv`.
  - Fit TF‑IDF vectorizer.
  - Fit optional SVD + Normalizer.
  - Fit kNN index/model.
  - Persist artifacts to disk (e.g., `movie_engine/artifacts/`): vectorizer, svd (optional), feature matrix, nn model, and the ordered titles list.
- [ ] Update runtime recommender code so Django only _loads_ artifacts (no fitting inside request handlers).
- [ ] Add a clear failure mode if artifacts are missing (developer-friendly message), or an explicit “build on startup” command for local convenience (do not auto-fit on request).
- [ ] Add a small test that builds artifacts from a tiny CSV and verifies they can be loaded and used to recommend.

### P2 — Tests

- [x] Add unit tests for recommender logic (tiny in-memory CSV).
- [x] Add view tests mocking OMDb calls (no network in tests).
- [x] Add/adjust a view test to assert `search_results` exists in context when a query is provided.

### Deliverable

- [x] Write/update `agents-md/backend.md` with summary + how to verify + perf notes.

### Acceptance Checks

- [x] Repeat searches do not rebuild TF‑IDF each time.
- [x] `python manage.py test` passes.
- [x] After a search, page shows shelves in order: Smart picks → Search results → Trending Now.
- [ ] No TF‑IDF/SVD/kNN fitting happens inside request/response.
- [ ] Artifacts can be built locally and then loaded by the app.
