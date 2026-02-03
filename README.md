# 📈 Habit Tracker with Visual Insights

A professional-grade Flask application to track daily habits, monitor streaks, and visualize progress using data analytics. Built with a focus on clean architecture and actionable insights.

## 🚀 Key Features
* **Habit Logging:** Easily create and track daily goals.
* **Streak Tracking:** Motivation through visual "streak" counters.
* **Visual Analytics:** Integrated charts to show completion trends over time.
* **Mood Correlation:** (In Progress) Analyzing how habits affect your daily wellbeing.

## 🛠️ Tech Stack
* **Backend:** Python 3.x, Flask (Application Factory Pattern)
* **Database:** SQLite with SQLAlchemy ORM (local dev, ignored in source control)
* **Frontend:** Jinja2 Templates & a small `static/css/style.css` for layout

## ⚙️ Running locally
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app in development:
   ```bash
   python app.py
   # or set FLASK_APP and use flask run
   ```

## ✅ Testing
Run the test suite with:
```bash
pip install -r requirements.txt
pytest -q
```

## Notes
- Tailwind-related build files and scripts are not required for the simplified UI and may be added later if you want a Tailwind workflow.
- The local SQLite DB lives in `instance/` and is ignored by git (`instance/*.db` in `.gitignore`).

## 📂 Project Structure
```text
├── instance/           # Database storage (local only)
├── static/             # CSS, JavaScript, and Images
├── templates/          # HTML Layouts (Jinja2)
├── app.py              # Application Factory & Routes
├── models.py           # Database Schema (Habits & Logs)
└── requirements.txt    # Project Dependenciesgot