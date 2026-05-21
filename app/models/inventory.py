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
# 1. inventory_items (物資品項) CRUD
# ==========================================

def create(data):
    """
    新增一筆物資記錄
    :param data: dict, 包含 group_id, name, unit, quantity, min_quantity, created_by
    :return: int, 新增記錄的 ID
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO inventory_items (group_id, name, unit, quantity, min_quantity, created_by) VALUES (?, ?, ?, ?, ?, ?)",
            (
                data.get('group_id'),
                data.get('name'),
                data.get('unit'),
                data.get('quantity', 0),
                data.get('min_quantity', 0),
                data.get('created_by')
            )
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except sqlite3.Error as e:
        print(f"Database error in inventory.create: {e}")
        raise e

def get_all():
    """
    取得所有物資記錄
    :return: list of sqlite3.Row
    """
    try:
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM inventory_items").fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in inventory.get_all: {e}")
        raise e

def get_by_id(item_id):
    """
    根據 ID 取得單筆物資記錄
    :param item_id: int, 物資 ID
    :return: sqlite3.Row or None
    """
    try:
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM inventory_items WHERE id = ?", (item_id,)).fetchone()
        conn.close()
        return row
    except sqlite3.Error as e:
        print(f"Database error in inventory.get_by_id: {e}")
        raise e

def update(item_id, data):
    """
    更新物資記錄（亦會自動更新 updated_at）
    :param item_id: int, 物資 ID
    :param data: dict, 包含欲更新的欄位
    :return: bool, 是否更新成功
    """
    try:
        conn = get_db_connection()
        fields = []
        values = []
        for key in ['group_id', 'name', 'unit', 'quantity', 'min_quantity', 'created_by']:
            if key in data:
                fields.append(f"{key} = ?")
                values.append(data[key])
        
        if not fields:
            conn.close()
            return False
            
        fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(item_id)
        sql = f"UPDATE inventory_items SET {', '.join(fields)} WHERE id = ?"
        cursor = conn.execute(sql, values)
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error in inventory.update: {e}")
        raise e

def delete(item_id):
    """
    刪除物資記錄
    :param item_id: int, 物資 ID
    :return: bool, 是否刪除成功
    """
    try:
        conn = get_db_connection()
        cursor = conn.execute("DELETE FROM inventory_items WHERE id = ?", (item_id,))
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error in inventory.delete: {e}")
        raise e

# ==========================================
# 2. inventory_logs (物資操作記錄) 輔助操作
# ==========================================

def create_log(data):
    """
    新增一筆物資入出庫操作記錄
    :param data: dict, 包含 item_id, user_id, action, quantity, note
    :return: int, 新增記錄的 ID
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO inventory_logs (item_id, user_id, action, quantity, note) VALUES (?, ?, ?, ?, ?)",
            (
                data.get('item_id'),
                data.get('user_id'),
                data.get('action'),
                data.get('quantity'),
                data.get('note')
            )
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except sqlite3.Error as e:
        print(f"Database error in inventory.create_log: {e}")
        raise e

def get_logs_by_item(item_id):
    """
    取得某物資的所有入出庫歷史記錄
    :param item_id: int, 物資 ID
    :return: list of sqlite3.Row
    """
    try:
        conn = get_db_connection()
        rows = conn.execute(
            "SELECT * FROM inventory_logs WHERE item_id = ? ORDER BY created_at DESC",
            (item_id,)
        ).fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in inventory.get_logs_by_item: {e}")
        raise e

def get_by_group(group_id):
    """
    取得特定群組的所有物資品項
    :param group_id: int, 群組 ID
    :return: list of sqlite3.Row
    """
    try:
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM inventory_items WHERE group_id = ? ORDER BY name ASC", (group_id,)).fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in inventory.get_by_group: {e}")
        raise e

