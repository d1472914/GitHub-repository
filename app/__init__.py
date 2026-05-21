import os
from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv

# 載入環境變數 (.env)
load_dotenv()

# 建立 LoginManager
login_manager = LoginManager()
login_manager.login_view = 'auth.login_page'
login_manager.login_message = '請先登入系統。'
login_manager.login_message_category = 'warning'

def create_app(test_config=None):
    """
    Flask App 工廠函式
    建立、設定並初始化 Flask 應用程式
    """
    app = Flask(__name__, instance_relative_config=True)

    # 預設配置
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'super_secret_key_for_development'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(app.instance_path, 'database.db')),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.from_mapping(test_config)

    # 確保 instance 目錄存在，用於存放 SQLite 資料庫
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

    return app
