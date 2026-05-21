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
# 1. expenses (共同開支) CRUD
# ==========================================

def create(data):
    """
    新增一筆共同開支記錄
    :param data: dict, 包含 group_id, title, amount, category, paid_by
    :return: int, 新增記錄的 ID
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (group_id, title, amount, category, paid_by) VALUES (?, ?, ?, ?, ?)",
            (
                data.get('group_id'),
                data.get('title'),
                data.get('amount'),
                data.get('category'),
                data.get('paid_by')
            )
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except sqlite3.Error as e:
        print(f"Database error in expense.create: {e}")
        raise e

def get_all():
    """
    取得所有共同開支記錄
    :return: list of sqlite3.Row
    """
    try:
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM expenses").fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in expense.get_all: {e}")
        raise e

def get_by_id(expense_id):
    """
    根據 ID 取得單筆共同開支記錄
    :param expense_id: int, 開支 ID
    :return: sqlite3.Row or None
    """
    try:
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
        conn.close()
        return row
    except sqlite3.Error as e:
        print(f"Database error in expense.get_by_id: {e}")
        raise e

def update(expense_id, data):
    """
    更新共同開支記錄
    :param expense_id: int, 開支 ID
    :param data: dict, 包含欲更新的欄位
    :return: bool, 是否更新成功
    """
    try:
        conn = get_db_connection()
        fields = []
        values = []
        for key in ['group_id', 'title', 'amount', 'category', 'paid_by']:
            if key in data:
                fields.append(f"{key} = ?")
                values.append(data[key])
        
        if not fields:
            conn.close()
            return False
            
        values.append(expense_id)
        sql = f"UPDATE expenses SET {', '.join(fields)} WHERE id = ?"
        cursor = conn.execute(sql, values)
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error in expense.update: {e}")
        raise e

def delete(expense_id):
    """
    刪除共同開支記錄
    :param expense_id: int, 開支 ID
    :return: bool, 是否刪除成功
    """
    try:
        conn = get_db_connection()
        cursor = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error in expense.delete: {e}")
        raise e

# ==========================================
# 2. expense_splits (開支分攤) 輔助操作
# ==========================================

def create_split(data):
    """
    新增一筆開支分攤記錄
    :param data: dict, 包含 expense_id, user_id, amount, is_settled
    :return: int, 新增記錄的 ID
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expense_splits (expense_id, user_id, amount, is_settled) VALUES (?, ?, ?, ?)",
            (
                data.get('expense_id'),
                data.get('user_id'),
                data.get('amount'),
                data.get('is_settled', 0)
            )
        )
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return new_id
    except sqlite3.Error as e:
        print(f"Database error in expense.create_split: {e}")
        raise e

def get_splits_by_expense(expense_id):
    """
    取得某筆開支的所有分攤記錄
    :param expense_id: int, 開支 ID
    :return: list of sqlite3.Row
    """
    try:
        conn = get_db_connection()
        rows = conn.execute(
            "SELECT * FROM expense_splits WHERE expense_id = ?",
            (expense_id,)
        ).fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in expense.get_splits_by_expense: {e}")
        raise e

def update_split(split_id, data):
    """
    更新單筆分攤記錄（如修改結清狀態）
    :param split_id: int, 分攤 ID
    :param data: dict, 包含欲更新的欄位 (如 is_settled)
    :return: bool, 是否更新成功
    """
    try:
        conn = get_db_connection()
        fields = []
        values = []
        for key in ['expense_id', 'user_id', 'amount', 'is_settled']:
            if key in data:
                fields.append(f"{key} = ?")
                values.append(data[key])
        
        if not fields:
            conn.close()
            return False
            
        values.append(split_id)
        sql = f"UPDATE expense_splits SET {', '.join(fields)} WHERE id = ?"
        cursor = conn.execute(sql, values)
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error in expense.update_split: {e}")
        raise e

def delete_splits_by_expense(expense_id):
    """
    刪除某筆開支的所有分攤記錄
    :param expense_id: int, 開支 ID
    :return: bool, 是否刪除成功
    """
    try:
        conn = get_db_connection()
        cursor = conn.execute("DELETE FROM expense_splits WHERE expense_id = ?", (expense_id,))
        conn.commit()
        rowcount = cursor.rowcount
        conn.close()
        return rowcount > 0
    except sqlite3.Error as e:
        print(f"Database error in expense.delete_splits_by_expense: {e}")
        raise e

def get_by_group(group_id):
    """
    取得特定群組的所有共同開支記錄
    :param group_id: int, 群組 ID
    :return: list of sqlite3.Row
    """
    try:
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM expenses WHERE group_id = ? ORDER BY created_at DESC", (group_id,)).fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in expense.get_by_group: {e}")
        raise e

def get_splits_by_group(group_id):
    """
    取得特定群組內所有開支的分攤記錄
    :param group_id: int, 群組 ID
    :return: list of sqlite3.Row
    """
    try:
        conn = get_db_connection()
        sql = """
            SELECT es.* FROM expense_splits es
            JOIN expenses e ON es.expense_id = e.id
            WHERE e.group_id = ?
        """
        rows = conn.execute(sql, (group_id,)).fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"Database error in expense.get_splits_by_group: {e}")
        raise e

