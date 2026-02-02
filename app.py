from flask import Flask, render_template
from models import db  # Import the db object we created in models.py
import os

def create_app():
    app = Flask(__name__)

    # 1. Database Configuration
    # This creates a folder called 'instance' and puts 'habits.db' inside it
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///habits.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 2. Initialize the Database with the App
    db.init_app(app)

    # 3. Create the Database Tables (The "Magic" Step)
    # This looks at models.py and creates the actual .db file
    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        # Later, we will fetch habits from the database here
        return render_template('index.html')

    return app

# The instance of our app
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)