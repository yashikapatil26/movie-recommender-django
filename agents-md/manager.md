## Manager Notes

### Working Agreement
- Backend agent owns: Python/Django logic + tests + data pipeline reliability.
- Frontend agent owns: Django templates (SSR) + a11y/UX feedback.
- Each agent reports results in:
	- `agents-md/backend.md`
	- `agents-md/frontend.md`

### Current Status (Implemented)
- Backend caching/refactor: TF‑IDF and dataset load are cached per-process.
- OMDb calls are cached per-title with timeouts and safe defaults.
- UI now preserves the query and shows a minimal “no results” message.
- Tests added; `python manage.py test` passes.
- Root `.gitignore` added to avoid committing local artifacts.

### Open Decisions
- Dataset: keep the tiny demo `movies.csv` vs regenerate/commit the ~5k dataset.
- Repo cleanup: delete the accidental `movies_raw.csv` HTML file and `movies_raw_files/` folder (currently ignored, but may still be tracked in git history).

### Review Checklist
- No UX scope creep: keep current layout/visual design.
- No network calls in tests.
- Repeat searches are faster than first search.
