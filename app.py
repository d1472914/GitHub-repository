import os
from dotenv import load_dotenv
from app import create_app
from app.models import db

# 優先載入 .env 中的環境變數
load_dotenv()

# 使用 Flask 工廠模式建立應用程式實例
app = create_app()

# 初始化資料庫，確保所有 SQLAlchemy 模型已載入並同步
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # 從環境變數讀取執行參數，或使用預設值
    host = os.environ.get('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 't']
    
    print(f"[*] Dormitory Co-living System starting... URL: http://{host}:{port} (Debug={debug})")
    app.run(host=host, port=port, debug=debug)
