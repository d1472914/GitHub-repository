import os
from dotenv import load_dotenv
from app import create_app

# 優先載入 .env 中的環境變數
load_dotenv()

# 使用 Flask 工廠模式建立應用程式實例
app = create_app()

if __name__ == '__main__':
    # Run server on port 5000
    app.run(
        host='0.0.0.0', 
        port=5000, 
        debug=os.environ.get('FLASK_DEBUG', 'True') == 'True'
    )
    # 從環境變數讀取執行參數，或使用預設值
    host = os.environ.get('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 't']
    
    print(f"[*] Dormitory Co-living System starting... URL: http://{host}:{port} (Debug={debug})")
    app.run(host=host, port=port, debug=debug)
