from app import create_app
from models import db, Habit, HabitLog


def test_index_and_add_habit():
    # Use in-memory DB for testing
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })

    client = app.test_client()

    # Index should load
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'Your Dashboard' in resp.data

    # Add a habit via JSON API
    resp = client.post('/add_habit', json={'name': 'Test Habit'})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['name'] == 'Test Habit'

    # After adding, the index should show the new habit
    resp = client.get('/')
    assert b'Test Habit' in resp.data


def test_calendar_and_day_endpoints():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    client = app.test_client()

    # Create habit
    resp = client.post('/add_habit', json={'name': 'Work'})
    habit = resp.get_json()
    hid = habit['id']

    # Add two logs on 2026-01-21 and one on 2026-02-05
    resp = client.post('/logs', json={'habit_id': hid, 'timestamp': '2026-01-21T10:00:00'})
    assert resp.status_code == 201
    resp = client.post('/logs', json={'habit_id': hid, 'timestamp': '2026-01-21T15:30:00'})
    assert resp.status_code == 201
    resp = client.post('/logs', json={'habit_id': hid, 'timestamp': '2026-02-05T09:00:00'})
    assert resp.status_code == 201

    # Calendar for Jan 2026 should include day 21
    resp = client.get('/calendar/2026/1')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 21 in data['days_with_logs']

    # Day details for Jan 21 should contain two logs
    resp = client.get('/day/2026/1/21')
    assert resp.status_code == 200
    d = resp.get_json()
    assert len(d['logs']) == 2
    times = [l['timestamp'] for l in d['logs']]
    assert any('10:00' in t for t in times)
    assert any('15:30' in t for t in times)


def test_delete_habit_and_log():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    client = app.test_client()

    # Create habit and a log
    resp = client.post('/add_habit', json={'name': 'ToDelete'})
    hid = resp.get_json()['id']
    resp = client.post('/logs', json={'habit_id': hid, 'timestamp': '2026-04-01T08:00:00'})
    logid = resp.get_json()['id']

    # Delete the log
    resp = client.delete(f'/logs/{logid}')
    assert resp.status_code == 200

    # Day should have no logs
    resp = client.get('/day/2026/4/1')
    assert resp.status_code == 200
    assert len(resp.get_json()['logs']) == 0

    # Delete habit
    resp = client.post('/delete_habit', json={'id': hid})
    assert resp.status_code == 200

    # Habit should no longer be on index
    resp = client.get('/')
    assert b'ToDelete' not in resp.data

def test_logs_with_timezone():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    client = app.test_client()

    # Create habit
    resp = client.post('/add_habit', json={'name': 'TZ Habit'})
    habit = resp.get_json()
    hid = habit['id']

    # Post a log with timezone offset
    resp = client.post('/logs', json={'habit_id': hid, 'timestamp': '2026-03-05T08:30:00+05:30'})
    assert resp.status_code == 201

    # Day details for 2026-03-05 should include the log
    resp = client.get('/day/2026/3/5')
    assert resp.status_code == 200
    d = resp.get_json()
    assert len(d['logs']) == 1
    assert 'TZ Habit' in d['logs'][0]['habit_name']


def test_nav_pages():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    client = app.test_client()

    routes = [
        ('/profile', 'Profile'),
        ('/streaks', 'Streaks'),
        ('/graph', 'Graph'),
        ('/insights', 'Insights'),
        ('/settings', 'Settings'),
        ('/help', 'Help'),
        ('/calendar', 'Calendar')
    ]

    for path, text in routes:
        resp = client.get(path)
        assert resp.status_code == 200
        assert (text.encode() in resp.data) or (text in resp.get_data(as_text=True))

