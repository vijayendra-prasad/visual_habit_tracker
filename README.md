# 📈 Habit Tracker with Visual Insights

A professional-grade Flask application to track daily habits, monitor streaks, and visualize progress using data analytics. Built with a focus on clean architecture and actionable insights.

## 🚀 Key Features
* **Habit Logging:** Easily create and track daily goals.
* **Streak Tracking:** Motivation through visual "streak" counters.
* **Visual Analytics:** Integrated charts to show completion trends over time.
* **Mood Correlation:** (In Progress) Analyzing how habits affect your daily wellbeing.

## 🛠️ Tech Stack
* **Backend:** Python 3.x, Flask (Application Factory Pattern)
* **Database:** SQLite with SQLAlchemy ORM
* **Frontend:** Jinja2 Templates, Tailwind CSS (built with Tailwind CLI + PostCSS for production)

Build Tailwind CSS locally:

1. Install dependencies (requires Node.js & npm):
   npm install
2. Build the CSS once:
   npm run build:css
3. For development, watch for changes:
   npm run watch:css

Note: the repo includes `src/input.css` (tailwind entry) and `tailwind.config.js`. The generated file is `static/css/tailwind.css` (currently a placeholder).

## ⚙️ Running in production (Waitress) ✅
For a lightweight, production-ready WSGI server on Windows, use **Waitress**:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start with Waitress (recommended):
   ```bash
   waitress-serve --listen=*:8000 app:app
   ```

Alternatively, run the provided helper script:
```bash
python run_waitress.py
```

This keeps the development server message from appearing and is better suited for actual deployments.

* **Version Control:** Git & GitHub

## 📂 Project Structure
```text
├── instance/           # Database storage (local only)
├── static/             # CSS, JavaScript, and Images
├── templates/          # HTML Layouts (Jinja2)
├── app.py              # Application Factory & Routes
├── models.py           # Database Schema (Habits & Logs)
└── requirements.txt    # Project Dependenciesgot