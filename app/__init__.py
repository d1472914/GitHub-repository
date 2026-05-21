import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(app.instance_path, 'database.db')),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize database
    db.init_app(app)

    # Simple root route for testing
    @app.route('/')
    def index():
        return "Roommate System - API Skeleton"

    return app
