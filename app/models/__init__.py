"""
Models 套件初始化
提供資料庫連線方法及匯入所有 Model 類別
"""

import os
import sqlite3

# 定義資料庫檔案路徑
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATABASE_PATH = os.path.join(BASE_DIR, 'instance', 'database.db')

def get_db_connection():
    """建立 SQLite 資料庫連線，並設定 row_factory 為 sqlite3.Row"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn
