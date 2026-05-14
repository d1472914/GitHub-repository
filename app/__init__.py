import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 初始化 SQLAlchemy 實例
db = SQLAlchemy()

def create_app(test_config=None):
    # 建立 Flask 實例
    app = Flask(__name__, instance_relative_config=True)
    
    # 預設設定
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'database.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
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

    # 初始化擴充套件
    db.init_app(app)

    # 註冊 Blueprints
    from app.routes import electricity
    app.register_blueprint(electricity.bp)

    # 註冊 CLI 命令，用於建立資料表
    @app.cli.command('init-db')
    def init_db_command():
        """清除舊資料並建立新資料表"""
        db.drop_all()
        db.create_all()
        # 建立預設房間假資料
        from app.models.electricity import Room
        if not Room.query.first():
            rooms = [Room(name='房間 A'), Room(name='房間 B'), Room(name='房間 C')]
            db.session.bulk_save_objects(rooms)
            db.session.commit()
            print("已建立預設房間 A, B, C")
        print('已初始化資料庫。')

    return app
