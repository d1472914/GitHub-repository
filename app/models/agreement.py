"""
Agreement Model — 公約資料模型 (sqlite3 版本)
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
        print(f"Database connection error in agreement model: {e}")
        raise e

def create(data):
    """
    建立新公約記錄
    :param data: dict, 包含 group_id, title, category, content, status, created_by
    :return: int 新增的公約 ID 或 None
    """
    sql = """
    INSERT INTO agreements (group_id, title, category, content, status, created_by)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (
                data.get('group_id'),
                data.get('title'),
                data.get('category'),
                data.get('content'),
                data.get('status', 'pending'),
                data.get('created_by')
            ))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error in create agreement: {e}")
        return None

def get_all():
    """
    取得所有公約記錄
    :return: list of Row
    """
    sql = "SELECT * FROM agreements"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_all agreements: {e}")
        return []

def get_by_group_id(group_id):
    """
    取得某個群組的所有公約記錄
    :param group_id: int, 群組 ID
    :return: list of Row
    """
    sql = "SELECT * FROM agreements WHERE group_id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (group_id,)).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_by_group_id agreements ({group_id}): {e}")
        return []
    finally:
        if conn:
            conn.close()

def update(agreement_id, data):
    """
    更新公約資料，若 content 有變動，則自動記錄新版本。
    
    Args:
        agreement_id (int): 公約 ID。
        data (dict): 更新的欄位與值（如 title, category, content, status, modified_by）。
        
    Returns:
        bool: 是否更新成功。
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 取得更新前舊資料
        cursor.execute("SELECT * FROM agreements WHERE id = ?", (agreement_id,))
        old_agreement = cursor.fetchone()
        if not old_agreement:
            return False
            
        fields = ["updated_at = CURRENT_TIMESTAMP"]
        params = {'id': agreement_id}
        
        # 動態欄位
        for key in ['title', 'category', 'content', 'status']:
            if key in data:
                fields.append(f"{key} = :{key}")
                params[key] = data[key]
                
        if len(fields) == 1: # 只有 updated_at
            return False
            
        sql = f"UPDATE agreements SET {', '.join(fields)} WHERE id = :id"
        cursor.execute(sql, params)
        
        # 若 content 有修改，新增版本歷史
        if 'content' in data and data['content'] != old_agreement['content']:
            # 取得目前的最新版本號
            cursor.execute("SELECT MAX(version_number) FROM agreement_versions WHERE agreement_id = ?", (agreement_id,))
            max_ver = cursor.fetchone()[0]
            next_ver = (max_ver or 1) + 1
            
            modified_by = data.get('modified_by', old_agreement['created_by'])
            
            version_sql = """
                INSERT INTO agreement_versions (agreement_id, version_number, content_before, content_after, modified_by)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(version_sql, (agreement_id, next_ver, old_agreement['content'], data['content'], modified_by))
            
            # 若公約內容被修改，且目前狀態是 active，可考慮重設同意狀態為 pending 讓室友重新投票
            if old_agreement['status'] == 'active':
                cursor.execute("UPDATE agreements SET status = 'pending' WHERE id = ?", (agreement_id,))
                # 清空原本的同意記錄
                cursor.execute("DELETE FROM agreement_approvals WHERE agreement_id = ?", (agreement_id,))
                
        conn.commit()
        return True
    except sqlite3.Error as e:
        logging.error(f"Error updating agreement: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def delete(agreement_id):
    """
    刪除公約（包括其關聯的所有版本與同意記錄）。
    
    Args:
        agreement_id (int): 公約 ID。
        
    Returns:
        bool: 是否刪除成功。
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 刪除關聯的 approvals 與 versions
        cursor.execute("DELETE FROM agreement_approvals WHERE agreement_id = ?", (agreement_id,))
        cursor.execute("DELETE FROM agreement_versions WHERE agreement_id = ?", (agreement_id,))
        # 刪除公約本體
        cursor.execute("DELETE FROM agreements WHERE id = ?", (agreement_id,))
        
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error deleting agreement: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

# --- 額外輔助函式：版本歷史與投票同意 ---

def get_versions(agreement_id):
    """
    取得特定公約的變更歷史。
    
    Args:
        agreement_id (int): 公約 ID。
        
    Returns:
        list: 版本記錄 sqlite3.Row 列表。
    """
    sql = "SELECT * FROM agreement_versions WHERE agreement_id = ? ORDER BY version_number DESC"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (agreement_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error getting agreement versions: {e}")
        return []
    finally:
        if conn:
            conn.close()

def approve(agreement_id, user_id):
    """
    記錄室友同意公約。
    
    Args:
        agreement_id (int): 公約 ID。
        user_id (int): 室友使用者 ID。
        
    Returns:
        bool: 是否投票成功。
    """
    sql = """
        INSERT OR IGNORE INTO agreement_approvals (agreement_id, user_id)
        VALUES (?, ?)
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (agreement_id, user_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error approving agreement: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def get_approvals(agreement_id):
    """
    取得已同意特定公約的室友記錄。
    
    Args:
        agreement_id (int): 公約 ID。
        
    Returns:
        list: 同意記錄列表，包含使用者暱稱。
    """
    sql = """
        SELECT a.*, u.nickname 
        FROM agreement_approvals a
        JOIN users u ON a.user_id = u.id
        WHERE a.agreement_id = ?
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (agreement_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error getting agreement approvals: {e}")
        return []
    finally:
        if conn:
            conn.close()


def get_by_id(agreement_id):
    """
    依 ID 取得單筆公約記錄
    :param agreement_id: int, 公約 ID
    :return: Row 或 None
    """
    sql = "SELECT * FROM agreements WHERE id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (agreement_id,)).fetchone()
    except sqlite3.Error as e:
        print(f"Error in get_by_id agreement ({agreement_id}): {e}")
        return None

def update(agreement_id, data):
    """
    更新公約資料
    :param agreement_id: int, 公約 ID
    :param data: dict, 需要更新的欄位值，例如 {'title': '新公約名稱', 'content': '新內容', 'status': 'active', 'updated_at': '...'}
    :return: bool 是否更新成功
    """
    if not data:
        return False
        
    keys = list(data.keys())
    # 自動補上更新時間欄位，若沒有帶的話
    if 'updated_at' not in keys:
        keys.append('updated_at')
        data['updated_at'] = sqlite3.Timestamp if hasattr(sqlite3, 'Timestamp') else 'CURRENT_TIMESTAMP'
        # 由於 CURRENT_TIMESTAMP 在預留字元中會作為字串寫入，這裡我們用 SQLite 內置函數在組裝時特別處理
        
    set_clauses = []
    params = []
    for key in keys:
        if key == 'updated_at' and data[key] == 'CURRENT_TIMESTAMP':
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        else:
            set_clauses.append(f"{key} = ?")
            params.append(data[key])
            
    set_clause = ", ".join(set_clauses)
    sql = f"UPDATE agreements SET {set_clause} WHERE id = ?"
    params.append(agreement_id)
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in update agreement ({agreement_id}): {e}")
        return False

def delete(agreement_id):
    """
    刪除公約記錄
    :param agreement_id: int, 公約 ID
    :return: bool 是否刪除成功
    """
    sql = "DELETE FROM agreements WHERE id = ?"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (agreement_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in delete agreement ({agreement_id}): {e}")
        return False
