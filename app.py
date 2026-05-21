import os
from app import create_app
from dotenv import load_dotenv

# 載入 .env 環境變數
load_dotenv()

# 建立 Flask 應用程式實例
app = create_app()

if __name__ == '__main__':
    # 讀取偵錯模式設定，預設為 True (開發環境)
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    
    # 啟動 Flask 伺服器
    app.run(
        host=os.environ.get('FLASK_RUN_HOST', '127.0.0.1'),
        port=int(os.environ.get('FLASK_RUN_PORT', 5000)),
        debug=debug_mode
    )
