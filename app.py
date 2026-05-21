import os
from app import create_app
from app.models import db

app = create_app()

# 初始化資料庫，建立所有定義的資料表
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # 執行 Flask 伺服器
    app.run(debug=True)
