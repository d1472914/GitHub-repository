import os
import sqlite3
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 建立 LoginManager
login_manager = LoginManager()
login_manager.login_view = 'auth.login_page'
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
        print("Database initialized successfully via schema.sql.")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

def create_app(test_config=None):
    """
    Flask App 工廠函式
    建立並設定 Flask 應用，初始化 SQLAlchemy 資料庫與註冊所有 Blueprint
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

    # 初始化 SQLAlchemy db
    from app.models import db
    db.init_app(app)

    # 初始化 LoginManager
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.get_by_id(int(user_id))

    # 註冊所有 Blueprint
    from app.routes import register_blueprints
    register_blueprints(app)

    # 執行資料庫初始化 (建立 schema.sql 中定義的 15 張表)
    init_db(app)

    # 根路由自動重導向至儀表板
    @app.route('/')
    def index():
        return redirect(url_for('dashboard.dashboard_page'))

    # 注入 app 變數至 Jinja2 全域上下文，供 base.html 偵測已註冊的 Blueprints
    @app.context_processor
    def inject_app():
        return dict(app=app)

    return app
