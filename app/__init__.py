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
from flask import Flask
from app.models import db
from app.routes import register_blueprints

def create_app(test_config=None):
    """
    Flask App 工廠函式
    建立並設定 Flask 應用，初始化資料庫與註冊所有 Blueprint
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # 載入預設設定與環境變數
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'roommate_cooperation_super_secret_key_2026_dev_only'),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'DATABASE_URL', 
            'sqlite:///' + os.path.join(app.instance_path, 'database.db')
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    
    if test_config is None:
        # 嘗試載入 instance 中的 config.py
        app.config.from_pyfile('config.py', silent=True)
    else:
        # 載入傳入的測試設定
        app.config.from_mapping(test_config)
        
    # 確保實例資料夾存在
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

        
    # 初始化 SQLAlchemy
    db.init_app(app)
    
    # 註冊所有模組化 Blueprint 路由
    register_blueprints(app)
    
    return app
