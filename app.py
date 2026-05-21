import os
from app import create_app, init_db

# 建立 Flask 應用程式實例
app = create_app()

# 初始化資料庫
with app.app_context():
    init_db()

if __name__ == '__main__':
    # 啟動開發伺服器
    app.run(debug=True)
