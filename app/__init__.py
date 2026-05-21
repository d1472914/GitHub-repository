import os
from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv

# 建立 LoginManager 實例
login_manager = LoginManager()
login_manager.login_view = 'auth.login_page'
login_manager.login_message = '請先登入系統。'
login_manager.login_message_category = 'warning'

def init_db():
    """初始化資料庫，執行 schema.sql 建立所有資料表"""
    import sqlite3
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    db_path = os.path.join(basedir, 'instance', 'database.db')
    schema_path = os.path.join(basedir, 'database', 'schema.sql')
    
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
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

def create_app():
    # 載入 .env 環境變數
    load_dotenv()
    
    app = Flask(__name__)
    
    # 基礎設定
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-roommate-system-12345')
    
    # 確保 instance 資料夾存在
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)
    
    login_manager.init_app(app)
    
    # 設定 user_loader，讀取登入使用者
    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(int(user_id))
        
    # 註冊所有 Blueprints
    from app.routes import register_blueprints
    register_blueprints(app)
    
    return app
