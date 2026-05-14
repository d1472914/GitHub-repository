import os
from flask import Flask

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
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 註冊 Blueprints
    from app import routes
    app.register_blueprint(routes.bp)

    return app
