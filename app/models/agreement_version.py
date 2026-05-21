"""
<<<<<<< HEAD
AgreementVersion Model — 公約版本歷史資料模型 (sqlite3 版本)
"""

import os
import sqlite3

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'instance', 'database.db')

def get_db_connection():
    """建立 SQLite 資料庫連線"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error in agreement_version model: {e}")
        raise e

def create(data):
    """
    建立新公約版本歷史記錄
    :param data: dict, 包含 agreement_id, version_number, content_before, content_after, modified_by
    :return: int 新增的版本記錄 ID 或 None
    """
    sql = """
    INSERT INTO agreement_versions (agreement_id, version_number, content_before, content_after, modified_by)
    VALUES (?, ?, ?, ?, ?)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (
                data.get('agreement_id'),
                data.get('version_number'),
                data.get('content_before'),
                data.get('content_after'),
                data.get('modified_by')
            ))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error in create agreement_version: {e}")
        return None

def get_all():
    """
    取得所有版本歷史記錄
    :return: list of Row
    """
    sql = "SELECT * FROM agreement_versions"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_all agreement_versions: {e}")
        return []

def get_by_agreement_id(agreement_id):
    """
    取得某公約的所有版本歷史，依版本號由大到小排序
    :param agreement_id: int, 公約 ID
    :return: list of Row
    """
    sql = "SELECT * FROM agreement_versions WHERE agreement_id = ? ORDER BY version_number DESC"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (agreement_id,)).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_by_agreement_id versions ({agreement_id}): {e}")
        return []

def get_by_id(version_id):
    """
    依 ID 取得單筆版本記錄
    :param version_id: int, 版本記錄 ID
    :return: Row 或 None
    """
    sql = "SELECT * FROM agreement_versions WHERE id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (version_id,)).fetchone()
    except sqlite3.Error as e:
        print(f"Error in get_by_id agreement_version ({version_id}): {e}")
        return None

def update(version_id, data):
    """
    更新版本記錄 (通常歷史記錄不常修改)
    :param version_id: int, 版本記錄 ID
    :param data: dict, 需要更新的欄位值
    :return: bool 是否更新成功
    """
    if not data:
        return False
        
    keys = list(data.keys())
    set_clause = ", ".join([f"{key} = ?" for key in keys])
    sql = f"UPDATE agreement_versions SET {set_clause} WHERE id = ?"
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            params = [data[key] for key in keys]
            params.append(version_id)
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in update agreement_version ({version_id}): {e}")
        return False

def delete(version_id):
    """
    刪除版本記錄
    :param version_id: int, 版本記錄 ID
    :return: bool 是否刪除成功
    """
    sql = "DELETE FROM agreement_versions WHERE id = ?"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (version_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in delete agreement_version ({version_id}): {e}")
        return False
=======
AgreementVersion Model — 公約版本歷史
每次公約修改時，記錄修改前後的差異
"""

from datetime import datetime
from app.models import db


class AgreementVersion(db.Model):
    __tablename__ = 'agreement_versions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    agreement_id = db.Column(db.Integer, db.ForeignKey('agreements.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    content_before = db.Column(db.Text, nullable=True)
    content_after = db.Column(db.Text, nullable=False)
    modified_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 關聯
    modifier = db.relationship('User', backref='agreement_modifications')

    def __repr__(self):
        return f'<AgreementVersion agreement={self.agreement_id} v{self.version_number}>'

    # ===== CRUD 方法 =====

    @classmethod
    def create(cls, agreement_id, version_number, content_after, modified_by, content_before=None):
        """建立新版本記錄"""
        version = cls(
            agreement_id=agreement_id,
            version_number=version_number,
            content_before=content_before,
            content_after=content_after,
            modified_by=modified_by
        )
        db.session.add(version)
        db.session.commit()
        return version

    @classmethod
    def get_all(cls):
        """取得所有版本記錄"""
        return cls.query.all()

    @classmethod
    def get_by_id(cls, version_id):
        """依 ID 取得版本"""
        return cls.query.get(version_id)

    @classmethod
    def get_by_agreement(cls, agreement_id):
        """取得某公約的所有版本（由新到舊）"""
        return cls.query.filter_by(agreement_id=agreement_id)\
            .order_by(cls.version_number.desc()).all()

    def update(self, **kwargs):
        """更新版本記錄"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        """刪除版本記錄"""
        db.session.delete(self)
        db.session.commit()
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
