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
    登錄一筆電費帳單。
    
    Args:
        data (dict): 包含 group_id, total_amount, total_kwh, period_start, period_end, created_by 的字典。
        
    Returns:
        int: 新增帳單的 id，若失敗則回傳 None。
    """
    sql = """
        INSERT INTO electricity_bills (group_id, total_amount, total_kwh, period_start, period_end, created_by)
        VALUES (:group_id, :total_amount, :total_kwh, :period_start, :period_end, :created_by)
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        params = {
            'group_id': data.get('group_id'),
            'total_amount': data.get('total_amount'),
            'total_kwh': data.get('total_kwh'),
            'period_start': data.get('period_start'),
            'period_end': data.get('period_end'),
            'created_by': data.get('created_by')
        }
        
        cursor.execute(sql, params)
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        logging.error(f"Error creating electricity bill: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def get_all():
    """
    取得所有電費帳單。
    
    Returns:
        list: 所有帳單記錄列表。
    """
    sql = "SELECT * FROM electricity_bills"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error getting all electricity bills: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_by_id(bill_id):
    """
    取得單筆電費帳單。
    
    Args:
        bill_id (int): 帳單 ID。
        
    Returns:
        sqlite3.Row: 電費帳單記錄。
    """
    sql = "SELECT * FROM electricity_bills WHERE id = ?"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (bill_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        logging.error(f"Error getting electricity bill by id: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_by_group(group_id):
    """
    取得群組的所有電費帳單，包含建立人暱稱。
    
    Args:
        group_id (int): 群組 ID。
        
    Returns:
        list: 帳單記錄列表。
    """
    sql = """
        SELECT b.*, u.nickname as created_by_name 
        FROM electricity_bills b
        JOIN users u ON b.created_by = u.id
        WHERE b.group_id = ?
        ORDER BY b.period_end DESC
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (group_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error getting electricity bills by group: {e}")
        return []
    finally:
        if conn:
            conn.close()

def update(bill_id, data):
    """
    更新電費帳單。
    
    Args:
        bill_id (int): 帳單 ID。
        data (dict): 更新的欄位（如 total_amount, total_kwh, period_start, period_end）。
        
    Returns:
        bool: 是否更新成功。
    """
    if not data:
        return False
        
    fields = []
    params = {'id': bill_id}
    for key in ['total_amount', 'total_kwh', 'period_start', 'period_end']:
        if key in data:
            fields.append(f"{key} = :{key}")
            params[key] = data[key]
            
    if not fields:
        return False
        
    sql = f"UPDATE electricity_bills SET {', '.join(fields)} WHERE id = :id"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error updating electricity bill: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def delete(bill_id):
    """
    刪除電費帳單，並自動刪除關聯的電表度數與分攤結果。
    
    Args:
        bill_id (int): 帳單 ID。
        
    Returns:
        bool: 是否刪除成功。
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM electricity_splits WHERE bill_id = ?", (bill_id,))
        cursor.execute("DELETE FROM meter_readings WHERE bill_id = ?", (bill_id,))
        cursor.execute("DELETE FROM electricity_bills WHERE id = ?", (bill_id,))
        
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error deleting electricity bill: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

# --- 額外輔助功能：電表度數與分攤結果 ---

def create_meter_reading(data):
    """
    登錄個人的電表度數。若已登錄，則更新它。
    
    Args:
        data (dict): 包含 bill_id, user_id, start_reading, end_reading 的字典。
        
    Returns:
        int: 插入或更新的記錄 id，若失敗則回傳 None。
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        bill_id = data.get('bill_id')
        user_id = data.get('user_id')
        start = float(data.get('start_reading', 0))
        end = float(data.get('end_reading', 0))
        kwh = end - start
        
        sql = """
            INSERT INTO meter_readings (bill_id, user_id, start_reading, end_reading, personal_kwh)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(bill_id, user_id) DO UPDATE SET
                start_reading = excluded.start_reading,
                end_reading = excluded.end_reading,
                personal_kwh = excluded.personal_kwh
        """
        cursor.execute(sql, (bill_id, user_id, start, end, kwh))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        logging.error(f"Error creating/updating meter reading: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def get_meter_readings(bill_id):
    """
    取得特定帳單的所有度數登錄，包含使用者暱稱。
    
    Args:
        bill_id (int): 帳單 ID。
        
    Returns:
        list: 度數登錄列表。
    """
    sql = """
        SELECT m.*, u.nickname 
        FROM meter_readings m
        JOIN users u ON m.user_id = u.id
        WHERE m.bill_id = ?
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (bill_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error getting meter readings: {e}")
        return []
    finally:
        if conn:
            conn.close()

def create_split(data):
    """
    建立電費分攤記錄。
    
    Args:
        data (dict): 包含 bill_id, user_id, personal_amount, shared_amount, total_amount, is_paid 的字典。
        
    Returns:
        int: 分攤記錄的 id。
    """
    sql = """
        INSERT INTO electricity_splits (bill_id, user_id, personal_amount, shared_amount, total_amount, is_paid)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (
            data.get('bill_id'),
            data.get('user_id'),
            data.get('personal_amount'),
            data.get('shared_amount'),
            data.get('total_amount'),
            data.get('is_paid', 0)
        ))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        logging.error(f"Error creating electricity split: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def get_splits(bill_id):
    """
    取得帳單的所有分攤結果，包含使用者暱稱。
    
    Args:
        bill_id (int): 帳單 ID。
        
    Returns:
        list: 電費分攤結果列表。
    """
    sql = """
        SELECT s.*, u.nickname 
        FROM electricity_splits s
        JOIN users u ON s.user_id = u.id
        WHERE s.bill_id = ?
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (bill_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error getting electricity splits: {e}")
        return []
    finally:
        if conn:
            conn.close()

def mark_split_paid(split_id):
    """
    標記電費分攤為已繳費。
    
    Args:
        split_id (int): 分攤 ID。
        
    Returns:
        bool: 是否更新成功。
    """
    sql = "UPDATE electricity_splits SET is_paid = 1 WHERE id = ?"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (split_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error marking electricity split as paid: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def get_db_connection():
    """建立並回傳 SQLite 資料庫連線，設定 Row factory 並啟用外鍵約束"""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, 'instance', 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# ==========================================
# 1. electricity_bills (電費帳單) CRUD
# ==========================================

def create(data):
    """
    新增一筆電費帳單記錄
    :param data: dict, 包含 group_id, total_amount, total_kwh, period_start, period_end, created_by
    :return: int, 新增記錄的 ID
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO electricity_bills (group_id, total_amount, total_kwh, period_start, period_end, created_by) VALUES (?, ?, ?, ?, ?, ?)",
            (
                data.get('group_id'),
                data.get('total_amount'),
                data.get('total_kwh'),
                data.get('period_start'),
                data.get('period_end'),
                data.get('created_by')
            )
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except sqlite3.Error as e:
        print(f"Database error in electricity.create: {e}")
        raise e

def get_all():
    """
    取得所有電費帳單記錄
    :return: list of sqlite3.Row
    """
    try:
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM electricity_bills").fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in electricity.get_all: {e}")
        raise e

def get_by_id(bill_id):
    """
    根據 ID 取得單筆電費帳單記錄
    :param bill_id: int, 帳單 ID
    :return: sqlite3.Row or None
    """
    try:
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM electricity_bills WHERE id = ?", (bill_id,)).fetchone()
        conn.close()
        return row
    except sqlite3.Error as e:
        print(f"Database error in electricity.get_by_id: {e}")
        raise e

def update(bill_id, data):
    """
    更新電費帳單記錄
    :param bill_id: int, 帳單 ID
    :param data: dict, 包含欲更新的欄位
    :return: bool, 是否更新成功
    """
    try:
        conn = get_db_connection()
        fields = []
        values = []
        for key in ['group_id', 'total_amount', 'total_kwh', 'period_start', 'period_end', 'created_by']:
            if key in data:
                fields.append(f"{key} = ?")
                values.append(data[key])
        
        if not fields:
            conn.close()
            return False
            
        values.append(bill_id)
        sql = f"UPDATE electricity_bills SET {', '.join(fields)} WHERE id = ?"
        cursor = conn.execute(sql, values)
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error in electricity.update: {e}")
        raise e

def delete(bill_id):
    """
    刪除電費帳單記錄（由於設有外鍵，且外鍵約束啟用，通常會級聯刪除或阻擋，具體取決於 SQLite schema 設定）
    :param bill_id: int, 帳單 ID
    :return: bool, 是否刪除成功
    """
    try:
        conn = get_db_connection()
        cursor = conn.execute("DELETE FROM electricity_bills WHERE id = ?", (bill_id,))
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error in electricity.delete: {e}")
        raise e

# ==========================================
# 2. meter_readings (電表度數) 輔助操作
# ==========================================

def create_reading(data):
    """
    新增一筆電表度數記錄
    :param data: dict, 包含 bill_id, user_id, start_reading, end_reading, personal_kwh
    :return: int, 新增記錄的 ID
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO meter_readings (bill_id, user_id, start_reading, end_reading, personal_kwh) VALUES (?, ?, ?, ?, ?)",
            (
                data.get('bill_id'),
                data.get('user_id'),
                data.get('start_reading'),
                data.get('end_reading'),
                data.get('personal_kwh')
            )
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except sqlite3.Error as e:
        print(f"Database error in electricity.create_reading: {e}")
        raise e

def get_readings_by_bill(bill_id):
    """
    取得某期電費帳單的所有電表度數登錄記錄
    :param bill_id: int, 帳單 ID
    :return: list of sqlite3.Row
    """
    try:
        conn = get_db_connection()
        rows = conn.execute(
            "SELECT * FROM meter_readings WHERE bill_id = ?",
            (bill_id,)
        ).fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in electricity.get_readings_by_bill: {e}")
        raise e

# ==========================================
# 3. electricity_splits (電費分攤) 輔助操作
# ==========================================

def create_split(data):
    """
    新增一筆電費分攤記錄
    :param data: dict, 包含 bill_id, user_id, personal_amount, shared_amount, total_amount, is_paid
    :return: int, 新增記錄的 ID
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO electricity_splits (bill_id, user_id, personal_amount, shared_amount, total_amount, is_paid) VALUES (?, ?, ?, ?, ?, ?)",
            (
                data.get('bill_id'),
                data.get('user_id'),
                data.get('personal_amount'),
                data.get('shared_amount'),
                data.get('total_amount'),
                data.get('is_paid', 0)
            )
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except sqlite3.Error as e:
        print(f"Database error in electricity.create_split: {e}")
        raise e

def get_splits_by_bill(bill_id):
    """
    取得某期電費帳單的所有分攤結果
    :param bill_id: int, 帳單 ID
    :return: list of sqlite3.Row
    """
    try:
        conn = get_db_connection()
        rows = conn.execute(
            "SELECT * FROM electricity_splits WHERE bill_id = ?",
            (bill_id,)
        ).fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in electricity.get_splits_by_bill: {e}")
        raise e

def update_split_status(split_id, is_paid):
    """
    更新某使用者的電費繳納狀態
    :param split_id: int, 電費分攤 ID
    :param is_paid: bool / int (0 或 1), 是否已付清
    :return: bool, 是否更新成功
    """
    try:
        conn = get_db_connection()
        cursor = conn.execute(
            "UPDATE electricity_splits SET is_paid = ? WHERE id = ?",
            (1 if is_paid else 0, split_id)
        )
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error in electricity.update_split_status: {e}")
        raise e

def get_by_group(group_id):
    """
    取得特定群組的所有電費帳單記錄
    :param group_id: int, 群組 ID
    :return: list of sqlite3.Row
    """
    try:
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM electricity_bills WHERE group_id = ? ORDER BY period_start DESC", (group_id,)).fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in electricity.get_by_group: {e}")
        raise e

