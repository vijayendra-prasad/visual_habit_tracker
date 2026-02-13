# Habit Tracker (Visual)

A lightweight Flask app for tracking daily habits with a simple, responsive UI and small reusable components. Focused on maintainability: no heavy UI frameworks, minimal JS, accessible markup, and mobile-first styling.

## Key features
- **User Profile Management**: Edit display name, email, and password with form validation and password strength indicator.
- Habit creation and simple logging (via form or JSON API).
- Calendar and day views (JSON endpoints for integration).
- Navigation pages: **Profile**, **Streaks**, **Graph**, **Insights**, **Settings**, **Help**, **Calendar** (placeholders ready for incremental enhancements).
- Responsive top navigation with an accessible **dark / light** theme toggle.
- Reusable UI components via Jinja macros (`templates/macros.html`) for cards, metrics, and lists.

## Tech stack
- Python 3.x, Flask (app factory pattern)
- SQLite with SQLAlchemy (local development)
- Minimal CSS (`static/css/style.css`) and small JS for nav + theme (`static/js/nav.js`)

## Running locally
1. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv .venv
   # Windows (PowerShell)
   .\.venv\Scripts\Activate
   # macOS / Linux
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app for development:
   ```bash
   python app.py
   # or use Flask CLI: $env:FLASK_APP = "app:create_app()"; flask run
   ```

## Tests & CI
- Run tests locally: `pytest -q` (tests are in `tests/`).
- GitHub Actions workflow (`.github/workflows/ci.yml`) runs tests on push/PR for Python 3.10/3.11.

## Project structure (high level)
```
├── app.py              # Application factory & routes
├── models.py           # SQLAlchemy models
├── templates/          # Jinja templates (includes `macros.html`)
├── static/             # CSS and small JS (nav + theme)
├── instance/           # local SQLite DB (ignored)
├── tests/              # pytest tests
└── requirements.txt    # Python deps
```

## Notes & future work
- The UI is intentionally minimal and optimized for small payloads; charts use lightweight SVG placeholders so you can incrementally add charting libraries when needed.
- Settings forms are present but not persisted yet — a small DB migration can add user preferences later.
- Keep sensitive config out of the repo — use `.env` or environment variables for production settings.

If you want, I can also add a short CONTRIBUTING guide and basic linting (flake8/black) to the repo.

## 📂 Project Structure
```text
├── instance/           # Database storage (local only)
├── static/             # CSS, JavaScript, and Images
├── templates/          # HTML Layouts (Jinja2)
├── app.py              # Application Factory & Routes
├── models.py           # Database Schema (Habits & Logs)
└── requirements.txt    # Project Dependenciesgot