import sqlite3
import os
import logging

def get_db_connection():
    """
    建立並回傳 SQLite 資料庫連線。
    資料庫路徑為 instance/database.db，並啟用外鍵約束與 Row factory。
    
    Returns:
        sqlite3.Connection: 資料庫連線物件
    """
    try:
        db_path = os.path.join(os.getcwd(), 'instance', 'database.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        logging.error(f"Database connection error: {e}")
        raise

def create(data):
    """
    新增一筆公約記錄。
    
    Args:
        data (dict): 包含 group_id, title, category, content, status, created_by 的字典。
        
    Returns:
        int: 新增公約的 id，若失敗則回傳 None。
    """
    sql = """
        INSERT INTO agreements (group_id, title, category, content, status, created_by)
        VALUES (:group_id, :title, :category, :content, :status, :created_by)
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        params = {
            'group_id': data.get('group_id'),
            'title': data.get('title'),
            'category': data.get('category'),
            'content': data.get('content'),
            'status': data.get('status', 'pending'),
            'created_by': data.get('created_by')
        }
        
        cursor.execute(sql, params)
        agreement_id = cursor.lastrowid
        
        # 寫入第一版到版本歷史
        version_sql = """
            INSERT INTO agreement_versions (agreement_id, version_number, content_before, content_after, modified_by)
            VALUES (?, 1, NULL, ?, ?)
        """
        cursor.execute(version_sql, (agreement_id, params['content'], params['created_by']))
        
        conn.commit()
        return agreement_id
    except sqlite3.Error as e:
        logging.error(f"Error creating agreement: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def get_all():
    """
    取得所有公約。
    
    Returns:
        list: 包含所有公約 sqlite3.Row 的列表。
    """
    sql = "SELECT * FROM agreements"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error getting all agreements: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_by_id(agreement_id):
    """
    取得單筆公約。
    
    Args:
        agreement_id (int): 公約 ID。
        
    Returns:
        sqlite3.Row: 公約記錄。
    """
    sql = "SELECT * FROM agreements WHERE id = ?"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (agreement_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        logging.error(f"Error getting agreement by id: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_by_group(group_id):
    """
    取得特定群組的所有公約。
    
    Args:
        group_id (int): 群組 ID。
        
    Returns:
        list: 公約記錄列表。
    """
    sql = "SELECT * FROM agreements WHERE group_id = ?"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (group_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error getting agreements by group: {e}")
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
