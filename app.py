from flask import Flask, render_template, request, redirect, url_for, jsonify, render_template_string, flash, session
from models import db, Habit, HabitLog, User  # Import models
from datetime import datetime, timedelta, timezone
import calendar
import re
import os
from pathlib import Path
from sqlalchemy.exc import OperationalError
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

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
            
            # Ensure 'profile_picture' column exists on user table
            res = db.session.execute(text("PRAGMA table_info('user')")).fetchall()
            cols = [r[1] for r in res]
            if 'profile_picture' not in cols:
                db.session.execute(text("ALTER TABLE user ADD COLUMN profile_picture VARCHAR(255)"))
                db.session.commit()
                print('Migration: added user.profile_picture column')
        except Exception as exc:
            # Fail silently but print to console for debugging (permission / non-sqlite DB)
            print('Migration check skipped:', exc)


# Validation Functions
def validate_display_name(name):
    """Validate display name. Returns error message or empty string if valid."""
    if not name or not name.strip():
        return ""  # Empty on GET requests, required only on POST
    if len(name) > 30:
        return "Full name cannot exceed 30 characters"
    return ""


def validate_email(email):
    """Validate email format. Returns error message or empty string if valid."""
    if not email or not email.strip():
        return ""  # Empty on GET requests, required only on POST
    
    # Pattern: A@A.A (A can be alphanumeric, period(.))
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return "Enter valid email address. Format: A@A.A (A can be alphanumeric, period(.))"
    return ""


def validate_password(password):
    """
    Validate password format. Returns error message or empty string if valid.
    Requirements: minimum 6 characters, at least one capital letter, one lowercase, one numeric.
    """
    if not password or not password.strip():
        return ""  # Password is optional (empty means keep current)
    
    if len(password) < 6:
        return "Password should be minimum 6 characters, with one capital letter, one small letter, one numeric"
    
    if not re.search(r'[a-z]', password):
        return "Password should be minimum 6 characters, with one capital letter, one small letter, one numeric"
    
    if not re.search(r'[A-Z]', password):
        return "Password should be minimum 6 characters, with one capital letter, one small letter, one numeric"
    
    if not re.search(r'\d', password):
        return "Password should be minimum 6 characters, with one capital letter, one small letter, one numeric"
    
    return ""


def validate_profile_picture(file):
    """Validate profile picture file. Returns error message or empty string if valid."""
    if not file or file.filename == '':
        return ""  # File is optional
    
    # Check file type
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    if not file.filename.lower().split('.')[-1] in allowed_extensions:
        return "Only image files are allowed"
    
    # Check file size (300KB)
    max_size = 300 * 1024  # 300KB in bytes
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > max_size:
        return "Image size should be less than 300kb"
    
    return ""


def save_profile_picture(file, user_id):
    """Save profile picture to disk. Returns filename or None if save failed."""
    if not file or file.filename == '':
        return None
    
    # Create upload directory if it doesn't exist
    upload_dir = Path('static/uploads/profile_pictures')
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate secure filename with user_id
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
    filename = f"user_{user_id}.{file_ext}"
    filepath = upload_dir / filename
    
    try:
        file.save(str(filepath))
        return filename
    except Exception as e:
        print(f"Error saving profile picture: {e}")
        return None


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
    @app.route('/profile', methods=['GET', 'POST'])
    def profile():
        # Get or create default user (ID=1 for demo)
        user = User.query.first()
        if not user:
            user = User(email='user@example.com', display_name='Your Name')
            db.session.add(user)
            db.session.commit()
        
        # Handle form submission
        if request.method == 'POST':
            display_name = request.form.get('display_name', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            profile_picture = request.files.get('profile_picture')
            
            # Validate inputs
            errors = {}
            
            # Check if fields are empty (required for submission)
            if not display_name:
                errors['display_name'] = "Full name is required"
            
            if not email:
                errors['email'] = "Email is required"
            
            # Only validate if fields have values
            if display_name and not errors.get('display_name'):
                name_error = validate_display_name(display_name)
                if name_error:
                    errors['display_name'] = name_error
            
            if email and not errors.get('email'):
                email_error = validate_email(email)
                if email_error:
                    errors['email'] = email_error
            
            # Validate password (only if provided)
            if password:
                password_error = validate_password(password)
                if password_error:
                    errors['password'] = password_error
            
            # Validate profile picture (only if provided)
            if profile_picture and profile_picture.filename:
                picture_error = validate_profile_picture(profile_picture)
                if picture_error:
                    errors['profile_picture'] = picture_error
            
            # If there are errors, re-render the form with error messages
            if errors:
                for field, error in errors.items():
                    flash(error, 'error')
                habits = Habit.query.order_by(Habit.created_at.desc()).all()
                recent_logs = HabitLog.query.order_by(HabitLog.timestamp.desc()).limit(5).all()
                streak = 0
                return render_template('profile.html', user=user, habits=habits, recent=recent_logs, streak=streak, errors=errors)
            
            # Update user data if all validations pass
            user.display_name = display_name
            user.email = email
            if password:
                user.password = generate_password_hash(password)
            
            # Save profile picture if provided
            if profile_picture and profile_picture.filename:
                filename = save_profile_picture(profile_picture, user.id)
                if filename:
                    user.profile_picture = filename
            
            user.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))
        
        # Compute lightweight context for display
        habits = Habit.query.order_by(Habit.created_at.desc()).all()
        recent_logs = HabitLog.query.order_by(HabitLog.timestamp.desc()).limit(5).all()
        # Simple streak calculation: longest consecutive days for now is placeholder
        streak = 0
        return render_template('profile.html', user=user, habits=habits, recent=recent_logs, streak=streak)

    @app.route('/profile/picture', methods=['DELETE'])
    def delete_profile_picture():
        """Delete the current user's profile picture"""
        user = User.query.first()
        if not user or not user.profile_picture:
            return jsonify({'error': 'No profile picture to delete'}), 400
        
        try:
            # Delete the file from disk
            upload_dir = Path('static/uploads/profile_pictures')
            file_path = upload_dir / user.profile_picture
            if file_path.exists():
                file_path.unlink()  # Delete the file
            
            # Update the database
            user.profile_picture = None
            user.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            
            return jsonify({'status': 'deleted', 'message': 'Profile picture deleted successfully'})
        except Exception as e:
            print(f"Error deleting profile picture: {e}")
            return jsonify({'error': 'Failed to delete profile picture'}), 500

    @app.route('/streaks')
    def streaks():
        # Provide simple items for UI cards
        # In future, replace with real analytics
        streak_items = [
            {'title': 'Longest Streak', 'value': '0', 'note': 'Long term best'},
            {'title': 'Current Streak', 'value': '0', 'note': 'Active days'},
            {'title': 'Best Habit', 'value': '—', 'note': 'Most consistent'}
        ]
        return render_template('streaks.html', streak_items=streak_items)

    @app.route('/graph')
    def graph():
        return render_template('graph.html')

    @app.route('/insights')
    def insights():
        # Placeholder insights - replace with analytic engine later
        insights = [
            {'title': 'Try a 7-day streak', 'body': 'Set a small daily goal to build momentum.'},
            {'title': 'Wear a reminder', 'body': 'Set a phone alarm or calendar reminder.'}
        ]
        return render_template('insights.html', insights=insights)

    @app.route('/settings', methods=['GET', 'POST'])
    def settings():
        # No persistent save yet; UI shows form that can be wired later
        return render_template('settings.html')

    @app.route('/help')
    def help_page():
        return render_template('help.html')

    @app.route('/calendar')
    def calendar_page():
        now = datetime.now(timezone.utc)
        return render_template('calendar_page.html', url=url_for('calendar_month', year=now.year, month=now.month))


def create_app(test_config=None):
    app = Flask(__name__)
    app.secret_key = app.config.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    if test_config:
        app.config.update(test_config)
    init_extensions(app)
    register_routes(app)
    return app

# The instance of our app for local running
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)