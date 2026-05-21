import os
import sqlite3
from flask import Flask, redirect, url_for
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '請先登入系統。'
login_manager.login_message_category = 'warning'

def init_db(app):
    """初始化 SQLite 資料庫，執行 schema.sql 建立所有資料表"""
    db_path = os.path.join(app.instance_path, 'database.db')
    schema_path = os.path.join(app.root_path, '..', 'database', 'schema.sql')
    
    os.makedirs(app.instance_path, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # 預設設定
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key_roommate_system'),
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    # Initialize extensions
    login_manager.init_app(app)

    from app.utils.auth_helpers import load_user_object

    @login_manager.user_loader
    def load_user(user_id):
        return load_user_object(user_id)

    from app.routes import register_blueprints
    register_blueprints(app)

    # 執行資料庫初始化
    init_db(app)

    @app.route('/')
    def index():
        return redirect(url_for('dashboard.index'))

    @app.route('/hello')
    def hello():
        return 'Hello, Roommate System!'

    return app
