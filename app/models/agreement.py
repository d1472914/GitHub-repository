import sqlite3
import os

def get_db_connection():
    """建立並回傳 SQLite 資料庫連線，設定 Row factory 並啟用外鍵約束"""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, 'instance', 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# ==========================================
# 1. agreements (公約主表) CRUD
# ==========================================

def create(data):
    """
    新增一筆公約記錄
    :param data: dict, 包含 group_id, title, category, content, status, created_by
    :return: int, 新增記錄的 ID
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO agreements (group_id, title, category, content, status, created_by) VALUES (?, ?, ?, ?, ?, ?)",
            (
                data.get('group_id'),
                data.get('title'),
                data.get('category'),
                data.get('content'),
                data.get('status', 'pending'),
                data.get('created_by')
            )
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except sqlite3.Error as e:
        print(f"Database error in agreement.create: {e}")
        raise e

def get_all():
    """
    取得所有公約記錄
    :return: list of sqlite3.Row
    """
    try:
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM agreements").fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in agreement.get_all: {e}")
        raise e

def get_by_id(agreement_id):
    """
    根據 ID 取得單筆公約記錄
    :param agreement_id: int, 公約 ID
    :return: sqlite3.Row or None
    """
    try:
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM agreements WHERE id = ?", (agreement_id,)).fetchone()
        conn.close()
        return row
    except sqlite3.Error as e:
        print(f"Database error in agreement.get_by_id: {e}")
        raise e

def update(agreement_id, data):
    """
    更新公約記錄（亦會自動更新 updated_at）
    :param agreement_id: int, 公約 ID
    :param data: dict, 包含欲更新的欄位
    :return: bool, 是否更新成功
    """
    try:
        conn = get_db_connection()
        fields = []
        values = []
        for key in ['group_id', 'title', 'category', 'content', 'status', 'created_by']:
            if key in data:
                fields.append(f"{key} = ?")
                values.append(data[key])
        
        if not fields:
            conn.close()
            return False
            
        fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(agreement_id)
        sql = f"UPDATE agreements SET {', '.join(fields)} WHERE id = ?"
        cursor = conn.execute(sql, values)
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error in agreement.update: {e}")
        raise e

def delete(agreement_id):
    """
    刪除公約記錄
    :param agreement_id: int, 公約 ID
    :return: bool, 是否刪除成功
    """
    try:
        conn = get_db_connection()
        cursor = conn.execute("DELETE FROM agreements WHERE id = ?", (agreement_id,))
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error in agreement.delete: {e}")
        raise e

# ==========================================
# 2. agreement_versions (版本歷史) 輔助操作
# ==========================================

def create_version(data):
    """
    新增一筆公約版本歷史記錄
    :param data: dict, 包含 agreement_id, version_number, content_before, content_after, modified_by
    :return: int, 新增記錄的 ID
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO agreement_versions (agreement_id, version_number, content_before, content_after, modified_by) VALUES (?, ?, ?, ?, ?)",
            (
                data.get('agreement_id'),
                data.get('version_number'),
                data.get('content_before'),
                data.get('content_after'),
                data.get('modified_by')
            )
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except sqlite3.Error as e:
        print(f"Database error in agreement.create_version: {e}")
        raise e

def get_versions_by_agreement(agreement_id):
    """
    取得某公約的所有版本歷史，依版本號排序
    :param agreement_id: int, 公約 ID
    :return: list of sqlite3.Row
    """
    try:
        conn = get_db_connection()
        rows = conn.execute(
            "SELECT * FROM agreement_versions WHERE agreement_id = ? ORDER BY version_number ASC",
            (agreement_id,)
        ).fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in agreement.get_versions_by_agreement: {e}")
        raise e

# ==========================================
# 3. agreement_approvals (同意記錄) 輔助操作
# ==========================================

def create_approval(data):
    """
    新增一筆公約同意記錄
    :param data: dict, 包含 agreement_id, user_id
    :return: int, 新增記錄的 ID
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO agreement_approvals (agreement_id, user_id) VALUES (?, ?)",
            (
                data.get('agreement_id'),
                data.get('user_id')
            )
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except sqlite3.Error as e:
        print(f"Database error in agreement.create_approval: {e}")
        raise e

def get_approvals_by_agreement(agreement_id):
    """
    取得某公約的所有同意記錄
    :param agreement_id: int, 公約 ID
    :return: list of sqlite3.Row
    """
    try:
        conn = get_db_connection()
        rows = conn.execute(
            "SELECT * FROM agreement_approvals WHERE agreement_id = ?",
            (agreement_id,)
        ).fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in agreement.get_approvals_by_agreement: {e}")
        raise e

def delete_approval(agreement_id, user_id):
    """
    刪除特定使用者的公約同意記錄
    :param agreement_id: int, 公約 ID
    :param user_id: int, 使用者 ID
    :return: bool, 是否刪除成功
    """
    try:
        conn = get_db_connection()
        cursor = conn.execute(
            "DELETE FROM agreement_approvals WHERE agreement_id = ? AND user_id = ?",
            (agreement_id, user_id)
        )
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error in agreement.delete_approval: {e}")
        raise e

def get_by_group(group_id):
    """
    取得特定群組的所有公約記錄
    :param group_id: int, 群組 ID
    :return: list of sqlite3.Row
    """
    try:
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM agreements WHERE group_id = ?", (group_id,)).fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in agreement.get_by_group: {e}")
        raise e

def delete_versions_by_agreement(agreement_id):
    """
    刪除特定公約的所有版本歷史記錄
    :param agreement_id: int, 公約 ID
    :return: bool, 是否刪除成功
    """
    try:
        conn = get_db_connection()
        cursor = conn.execute("DELETE FROM agreement_versions WHERE agreement_id = ?", (agreement_id,))
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error in agreement.delete_versions_by_agreement: {e}")
        raise e


