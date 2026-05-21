import os
from flask import Flask
<<<<<<< HEAD
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
=======

def create_app(test_config=None):
    # 建立 Flask 實例
    app = Flask(__name__, instance_relative_config=True)
    
    # 預設設定
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        # 載入額外設定 (如果有的話)
        app.config.from_pyfile('config.py', silent=True)
    else:
        # 載入測試設定
        app.config.from_mapping(test_config)

    # 確保 instance 資料夾存在
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
    
from flask_login import LoginManager

db = SQLAlchemy()

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key_roommate_system'),
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(app.instance_path, 'database.db')}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
<<<<<<< HEAD
        
    # 初始化 SQLAlchemy
    db.init_app(app)
    
    # 註冊所有模組化 Blueprint 路由
    register_blueprints(app)
    
=======

    # Initialize database
    db.init_app(app)

    # Simple root route for testing
    @app.route('/')
    def index():
        return "Roommate System - API Skeleton"
    # 註冊 Blueprints
    from app import routes
    app.register_blueprint(routes.bp)
    # Initialize extensions
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from app.utils.auth_helpers import load_user_object

    @login_manager.user_loader
    def load_user(user_id):
        return load_user_object(user_id)

    from app.routes import register_blueprints
    register_blueprints(app)

    @app.route('/hello')
    def hello():
        return 'Hello, Roommate System!'

>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
    return app
