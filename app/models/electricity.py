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

