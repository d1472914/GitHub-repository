import os
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
        
    # 初始化 SQLAlchemy
    db.init_app(app)
    
    # 註冊所有模組化 Blueprint 路由
    register_blueprints(app)
    
    @app.route('/')
    def index():
        from flask import session, redirect, url_for
        if 'user_id' in session:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login_page'))
    
    return app

