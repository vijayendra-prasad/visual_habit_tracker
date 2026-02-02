# Copilot / Agent Instructions for this repo ✅

## Quick snapshot (current state)
- Date: 2026-02-02
- Repository currently contains no committed source files or CI config. Terminal history suggests an intended Flask app with: `app.py`, `models.py`, `templates/`, `static/`, `requirements.txt`.

> Note: This file is intentionally conservative — it documents *what to look for* and *how to act* when files are present. Update this document when concrete patterns appear in source.

---

## High-level goal for agents 🔎
- Make minimal, testable changes that keep the code runnable locally.
- Prefer small PRs with a short description and a test demonstrating behavior change.

## When you start working locally 🛠️
1. Create and activate a venv:
   - Windows: `python -m venv .venv && .\.venv\Scripts\Activate`
2. Install deps: `pip install -r requirements.txt` (if `requirements.txt` exists). If there is a `pyproject.toml` / `poetry.lock`, follow those instead.
3. Common dev run commands:
   - If an `app.py` exposes `app` or sets `if __name__ == "__main__": app.run(...)` → `python app.py`.
   - If the repo uses Flask CLI (`create_app` or `FLASK_APP`), use:
     - Windows (PowerShell): `$env:FLASK_APP = "app:create_app()"; flask run` or `python -m flask run` after setting env.
4. If `.env` exists or `python-dotenv` in deps, load it before running.

## What to detect and how to act (automated heuristics) 🤖
- Entry points
  - If `app.py` exists and contains `def create_app(` → treat code as factory-style app. Use `FLASK_APP="app:create_app()"` to run.
  - If `app` variable is present at module level, use `FLASK_APP=app.py` or `python app.py`.
- Database
  - If `models.py` imports `flask_sqlalchemy` or defines `db = SQLAlchemy()`, look for a `migrations/` folder or `Flask-Migrate` in requirements. For DB-migration changes, add/adjust Alembic/Flask-Migrate scripts and test migrations locally.
- Templates/static
  - Standard Flask layout: `templates/` and `static/`. Verify Jinja patterns by searching for `render_template(` and `url_for('static'`.
- Tests
  - If `tests/` exists, run `pytest -q`. Add tests for bug fixes and new features.
- CI / Workflows
  - If `.github/workflows` appears, mirror workflow steps locally (install, test, lint).

## Code-style & tooling (project-specific heuristics) 🔧
- If `black`, `flake8`, or `pre-commit` is present in `requirements.txt` or config files, run them before committing.
- If `pyproject.toml` or `tox.ini` exists, prefer their declared commands for test/lint tasks.

## PR / commit guidance ✍️
- Keep PRs small and focused. Each PR should have at least one test demonstrating the change when applicable.
- Write a one-line summary and a short description that links to the related issue or rationale.

## Security & secrets ⚠️
- Refuse to commit secrets. If you detect `.env` with secrets, suggest adding `.env` to `.gitignore` and using environment variables or secrets management.

## What I (the agent) should record for future improvements 📚
- When files appear (e.g., `app.py`, `models.py`), update this doc with concrete code snippets and examples from the codebase (e.g., app factory name, database URL format, custom CLI commands).
- If a non-standard layout is introduced (blueprints under `src/` or `service/`), add explicit run/test commands and directory map.

---

If you'd like, I can:
- Scan the repository again after you add files and update this document with specific, concrete examples (endpoints, DB models, tests, and commands). ✅

Please tell me which files you plan to add next (or push a commit), and I will immediately re-scan and refine these instructions.