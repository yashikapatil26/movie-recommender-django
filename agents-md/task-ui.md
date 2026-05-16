## Frontend Task List (Owner: Frontend Agent)

**Goal**: Keep the existing look/layout, but improve empty states and accessibility (no redesign).

**New Feature Goal**: After searching, render shelves in this order:

1. Smart picks for "<query>" (existing)
2. Search results for "<query>" (new)
3. Trending Now (existing)

### P0 — Empty/Error States

- [x] Show a minimal inline message when a query is present but recommendations are empty.
- [x] Preserve the user’s query in the search box after submit.

### P0 — Search Results Shelf (New)

- [x] Add a second shelf titled `Search results for "{{ query }}"`.
- [x] Render `search_results` cards using the existing card layout (same poster/meta guards).
- [x] Ensure this shelf only appears when a query is present and `search_results` is non-empty.
- [x] Ensure visual ordering is: Smart picks section → Search results section → Trending Now.

### P1 — Accessibility & Polish

- [x] Add an accessible label for the search input.
- [x] Add `alt` text for posters and `loading="lazy"`.

### P2 — Resilience

- [x] Ensure poster is always present via backend placeholder fallback.
- [x] (Optional) Guard rating/year/genre display when values are missing/`N/A` (low priority).

### Deliverable

- [x] Write/update `agents-md/frontend.md` with summary + manual checks.
