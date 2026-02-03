from flask import Flask, render_template, request, redirect, url_for, jsonify, render_template_string
from models import db, Habit, HabitLog  # Import models
from datetime import datetime, timedelta, timezone
import calendar
from sqlalchemy.exc import OperationalError

def init_extensions(app):
    # Default Database Configuration (can be overridden by test_config)
    app.config.setdefault('SQLALCHEMY_DATABASE_URI', 'sqlite:///habits.db')
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)

    db.init_app(app)
    with app.app_context():
        db.create_all()
        # Simple schema migration for local SQLite DBs: ensure 'timestamp' column exists
        try:
            from sqlalchemy import text

            # Use PRAGMA to inspect columns for sqlite; if missing, add column and populate from date
            res = db.session.execute(text("PRAGMA table_info('habit_log')")).fetchall()
            cols = [r[1] for r in res]
            if 'timestamp' not in cols:
                db.session.execute(text("ALTER TABLE habit_log ADD COLUMN timestamp DATETIME"))
                # Populate existing rows with the date at midnight UTC (no timezone info)
                db.session.execute(text("UPDATE habit_log SET timestamp = date || ' 00:00:00' WHERE timestamp IS NULL"))
                db.session.commit()
                print('Migration: added habit_log.timestamp column')
        except Exception as exc:
            # Fail silently but print to console for debugging (permission / non-sqlite DB)
            print('Migration check skipped:', exc)


def register_routes(app):
    @app.route('/')
    def index():
        # Fetch habits newest-first
        habits = Habit.query.order_by(Habit.created_at.desc()).all()
        habits_json = [{'id': h.id, 'name': h.name} for h in habits]
        return render_template('index.html', habits=habits, habits_json=habits_json)

    @app.route('/add_habit', methods=['POST'])
    def add_habit():
        # Accept form data or JSON
        if request.is_json:
            payload = request.get_json()
            name = payload.get('name', '').strip()
        else:
            name = request.form.get('name', '').strip()

        if not name:
            # Bad request
            if request.is_json:
                return jsonify({'error': 'Name required'}), 400
            return redirect(url_for('index'))

        # Create and save
        new_habit = Habit(name=name)
        db.session.add(new_habit)
        db.session.commit()

        if request.is_json:
            return jsonify({'id': new_habit.id, 'name': new_habit.name, 'created_at': new_habit.created_at.isoformat()}), 201

        return redirect(url_for('index'))

    @app.route('/delete_habit', methods=['POST'])
    def delete_habit():
        payload = request.get_json() or {}
        hid = payload.get('id')
        if not hid:
            return jsonify({'error': 'id required'}), 400
        habit = db.session.get(Habit, hid)
        if not habit:
            return jsonify({'error': 'not found'}), 404
        db.session.delete(habit)
        db.session.commit()
        return jsonify({'status': 'deleted'})

    @app.route('/logs/<int:log_id>', methods=['DELETE'])
    def delete_log(log_id):
        log = db.session.get(HabitLog, log_id)
        if not log:
            return jsonify({'error': 'not found'}), 404
        db.session.delete(log)
        db.session.commit()
        return jsonify({'status': 'deleted'})

    @app.route('/calendar/<int:year>/<int:month>')
    def calendar_month(year, month):
        # Return list of days in the month which have any HabitLog entries
        try:
            start = datetime(year, month, 1, tzinfo=timezone.utc)
        except ValueError:
            return jsonify({'error': 'Invalid month/year'}), 400
        _, days_in_month = calendar.monthrange(year, month)
        end = start + timedelta(days=days_in_month)

        try:
            logs = HabitLog.query.filter(HabitLog.timestamp >= start, HabitLog.timestamp < end).all()
        except OperationalError:
            # If DB schema is older and timestamp column is missing, return empty list instead of 500
            return jsonify({'days_with_logs': []})

        days = sorted({log.timestamp.astimezone(timezone.utc).day for log in logs})
        return jsonify({'days_with_logs': days})

    @app.route('/day/<int:year>/<int:month>/<int:day>')
    def day_details(year, month, day):
        try:
            day_start = datetime(year, month, day, tzinfo=timezone.utc)
        except ValueError:
            return jsonify({'error': 'Invalid date'}), 400
        day_end = day_start + timedelta(days=1)

        try:
            logs = HabitLog.query.filter(HabitLog.timestamp >= day_start, HabitLog.timestamp < day_end).order_by(HabitLog.timestamp.asc()).all()
        except OperationalError:
            # Old DB schema without timestamp -> return empty list
            return jsonify({'logs': []})

        out = []
        for log in logs:
            out.append({
                'id': log.id,
                'habit_id': log.habit_id,
                'habit_name': log.habit.name,
                'timestamp': log.timestamp.isoformat()
            })
        return jsonify({'logs': out})

    @app.route('/logs', methods=['POST'])
    def add_log():
        payload = request.get_json() or {}
        habit_id = payload.get('habit_id')
        timestamp = payload.get('timestamp')  # ISO8601

        if not habit_id:
            return jsonify({'error': 'habit_id required'}), 400

        # Use session.get for SQLAlchemy 2.x compatibility
        habit = db.session.get(Habit, habit_id)
        if not habit:
            return jsonify({'error': 'habit not found'}), 404

        if timestamp:
            try:
                ts = datetime.fromisoformat(timestamp)
                # If naive, assume UTC
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
            except Exception:
                return jsonify({'error': 'Invalid timestamp'}), 400
        else:
            ts = datetime.now(timezone.utc)

        # Create HabitLog
        log = HabitLog(habit_id=habit_id, timestamp=ts, date=ts.date())
        db.session.add(log)
        db.session.commit()

        return jsonify({'id': log.id, 'habit_id': log.habit_id, 'habit_name': habit.name, 'timestamp': log.timestamp.isoformat()}), 201

    # Minimal placeholder pages for UI navigation links
    @app.route('/profile')
    def profile():
        return render_template_string("{% extends 'base.html' %}{% block content %}<h2>Profile</h2><p>Profile details coming soon.</p>{% endblock %}")

    @app.route('/streaks')
    def streaks():
        return render_template_string("{% extends 'base.html' %}{% block content %}<h2>Streaks</h2><p>Your streaks will be visualized here.</p>{% endblock %}")

    @app.route('/graph')
    def graph():
        return render_template_string("{% extends 'base.html' %}{% block content %}<h2>Graph</h2><p>Graphs and trends will be available here.</p>{% endblock %}")

    @app.route('/insights')
    def insights():
        return render_template_string("{% extends 'base.html' %}{% block content %}<h2>Insights</h2><p>Insights and suggestions will appear here.</p>{% endblock %}")

    @app.route('/settings')
    def settings():
        return render_template_string("{% extends 'base.html' %}{% block content %}<h2>Settings</h2><p>App settings and preferences.</p>{% endblock %}")

    @app.route('/help')
    def help_page():
        return render_template_string("{% extends 'base.html' %}{% block content %}<h2>Help</h2><p>Documentation and support links.</p>{% endblock %}")

    @app.route('/calendar')
    def calendar_page():
        now = datetime.now(timezone.utc)
        return render_template_string(
            "{% extends 'base.html' %}{% block content %}<h2>Calendar</h2><p><a href='{{ url }}'>View current month data (JSON)</a></p>{% endblock %}",
            url=url_for('calendar_month', year=now.year, month=now.month)
        )


def create_app(test_config=None):
    app = Flask(__name__)
    if test_config:
        app.config.update(test_config)
    init_extensions(app)
    register_routes(app)
    return app

# The instance of our app for local running
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)