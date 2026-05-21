<<<<<<< HEAD
"""
Expense Model — 共同開支資料模型 (sqlite3 版本)
"""

import os
import sqlite3

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'instance', 'database.db')

def get_db_connection():
    """建立 SQLite 資料庫連線"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
=======
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
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
<<<<<<< HEAD
        print(f"Database connection error in expense model: {e}")
        raise e

def create(data):
    """
    建立新開支記錄
    :param data: dict, 包含 group_id, title, amount, category, paid_by
    :return: int 新增的開支 ID 或 None
    """
    sql = """
    INSERT INTO expenses (group_id, title, amount, category, paid_by)
    VALUES (?, ?, ?, ?, ?)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (
=======
        logging.error(f"Database connection error: {e}")
        raise

def create(data):
    """
    新增一筆共同開支記錄，並動態分攤給指定/全部成員。
    
    Args:
        data (dict): 包含 group_id, title, amount, category, paid_by 的字典。
                     可選包含 splits 列表，每個 split 是包含 user_id 和 amount 的 dict。
                     若未傳入 splits，則預設均攤給群組內的所有成員。
        
    Returns:
        int: 新增開支的 id，若失敗則回傳 None。
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. 寫入 expense
        expense_sql = """
            INSERT INTO expenses (group_id, title, amount, category, paid_by)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor.execute(expense_sql, (
            data.get('group_id'),
            data.get('title'),
            data.get('amount'),
            data.get('category'),
            data.get('paid_by')
        ))
        expense_id = cursor.lastrowid
        
        # 2. 處理分攤 splits
        splits = data.get('splits')
        paid_by = data.get('paid_by')
        
        if not splits:
            # 預設：均攤給群組裡的所有成員
            cursor.execute("SELECT id FROM users WHERE group_id = ?", (data.get('group_id'),))
            members = cursor.fetchall()
            if members:
                member_count = len(members)
                split_amount = round(data.get('amount') / member_count, 2)
                
                splits = []
                for m in members:
                    # 如果是被分攤者等於付款者本人，預設 is_settled = 1 (自己付給自己的部分自動結清)
                    # 這裡為了簡化計算，我們仍寫入 split，但若 user_id == paid_by，可以標記為 is_settled = 1
                    is_settled = 1 if m['id'] == paid_by else 0
                    splits.append({
                        'user_id': m['id'],
                        'amount': split_amount,
                        'is_settled': is_settled
                    })
                    
        # 寫入 expense_splits
        split_sql = """
            INSERT INTO expense_splits (expense_id, user_id, amount, is_settled)
            VALUES (?, ?, ?, ?)
        """
        for s in splits:
            # 若 split dict 中沒特別指定 is_settled，則預設若 user_id == paid_by 為 1，否則為 0
            is_settled = s.get('is_settled', 1 if s.get('user_id') == paid_by else 0)
            cursor.execute(split_sql, (expense_id, s.get('user_id'), s.get('amount'), is_settled))
            
        conn.commit()
        return expense_id
    except sqlite3.Error as e:
        logging.error(f"Error creating expense: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def get_all():
    """
    取得所有開支。
    
    Returns:
        list: 所有開支記錄列表。
    """
    sql = "SELECT * FROM expenses"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error getting all expenses: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_by_id(expense_id):
    """
    取得單筆開支。
    
    Args:
        expense_id (int): 開支 ID。
        
    Returns:
        sqlite3.Row: 開支記錄。
    """
    sql = "SELECT * FROM expenses WHERE id = ?"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (expense_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        logging.error(f"Error getting expense by id: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_by_group(group_id):
    """
    取得特定群組的所有開支，包含付款人暱稱。
    
    Args:
        group_id (int): 群組 ID。
        
    Returns:
        list: 開支記錄列表。
    """
    sql = """
        SELECT e.*, u.nickname as paid_by_name 
        FROM expenses e
        JOIN users u ON e.paid_by = u.id
        WHERE e.group_id = ?
        ORDER BY e.created_at DESC
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (group_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error getting expenses by group: {e}")
        return []
    finally:
        if conn:
            conn.close()

def update(expense_id, data):
    """
    更新開支資料。
    注意：這僅更新 expenses 表本身。
    
    Args:
        expense_id (int): 開支 ID。
        data (dict): 更新的欄位（如 title, amount, category, paid_by）。
        
    Returns:
        bool: 是否更新成功。
    """
    if not data:
        return False
        
    fields = []
    params = {'id': expense_id}
    for key in ['title', 'amount', 'category', 'paid_by']:
        if key in data:
            fields.append(f"{key} = :{key}")
            params[key] = data[key]
            
    if not fields:
        return False
        
    sql = f"UPDATE expenses SET {', '.join(fields)} WHERE id = :id"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error updating expense: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def delete(expense_id):
    """
    刪除開支與其關聯的所有分攤。
    
    Args:
        expense_id (int): 開支 ID。
        
    Returns:
        bool: 是否刪除成功。
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM expense_splits WHERE expense_id = ?", (expense_id,))
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error deleting expense: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

# --- 額外輔助功能：分攤與結帳 ---

def create_split(data):
    """
    手動建立一筆分攤記錄。
    
    Args:
        data (dict): 包含 expense_id, user_id, amount, is_settled 的字典。
        
    Returns:
        int: 新增分攤記錄的 id。
    """
    sql = """
        INSERT INTO expense_splits (expense_id, user_id, amount, is_settled)
        VALUES (?, ?, ?, ?)
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (
            data.get('expense_id'),
            data.get('user_id'),
            data.get('amount'),
            data.get('is_settled', 0)
        ))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        logging.error(f"Error creating expense split: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def get_splits(expense_id):
    """
    取得特定開支的所有分攤明細，包含使用者暱稱。
    
    Args:
        expense_id (int): 開支 ID。
        
    Returns:
        list: 分攤明細列表。
    """
    sql = """
        SELECT s.*, u.nickname 
        FROM expense_splits s
        JOIN users u ON s.user_id = u.id
        WHERE s.expense_id = ?
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (expense_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error getting expense splits: {e}")
        return []
    finally:
        if conn:
            conn.close()

def settle_split(split_id):
    """
    標記特定的分攤記錄為已結清。
    
    Args:
        split_id (int): 分攤記錄 ID。
        
    Returns:
        bool: 是否結清成功。
    """
    sql = "UPDATE expense_splits SET is_settled = 1 WHERE id = ?"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (split_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error settling split: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def settle_group_expenses(group_id, user_id):
    """
    結清群組內某人所有的未結帳分攤（不論是別人欠他的，還是他欠別人的）。
    
    Args:
        group_id (int): 群組 ID。
        user_id (int): 使用者 ID。
        
    Returns:
        bool: 是否成功。
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. 結清此人欠別人的分攤
        sql1 = """
            UPDATE expense_splits 
            SET is_settled = 1 
            WHERE user_id = ? AND is_settled = 0 AND expense_id IN (
                SELECT id FROM expenses WHERE group_id = ?
            )
        """
        cursor.execute(sql1, (user_id, group_id))
        
        # 2. 結清別人欠此人的分攤
        sql2 = """
            UPDATE expense_splits 
            SET is_settled = 1 
            WHERE is_settled = 0 AND expense_id IN (
                SELECT id FROM expenses WHERE group_id = ? AND paid_by = ?
            )
        """
        cursor.execute(sql2, (group_id, user_id))
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        logging.error(f"Error settling group expenses for user {user_id}: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def get_group_balances(group_id):
    """
    計算群組內各成員未結清的財務餘額。
    
    A 的「應收金額」 = 所有 A 付款的 expense 裡，其他成員未結清 (is_settled=0 且 user_id != A) 的分攤金額加總。
    A 的「應付金額」 = 所有其他人付款的 expense 裡，分攤給 A 且未結清 (is_settled=0 且 user_id = A) 的金額加總。
    A 的「淨額」 = 應收 - 應付
    
    Args:
        group_id (int): 群組 ID。
        
    Returns:
        dict: 鍵為 user_id，值為含有 'nickname', 'receivable', 'payable', 'net' 的 dict。
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 取得群組所有成員
        cursor.execute("SELECT id, nickname FROM users WHERE group_id = ?", (group_id,))
        users = cursor.fetchall()
        
        balances = {}
        for u in users:
            uid = u['id']
            balances[uid] = {
                'id': uid,
                'nickname': u['nickname'],
                'receivable': 0.0,
                'payable': 0.0,
                'net': 0.0
            }
            
        # 1. 計算每個人的應收 (即此人付的款，但別人還沒結清給他的部分)
        receivable_sql = """
            SELECT e.paid_by, SUM(s.amount) as total_receivable
            FROM expense_splits s
            JOIN expenses e ON s.expense_id = e.id
            WHERE e.group_id = ? AND s.is_settled = 0 AND s.user_id != e.paid_by
            GROUP BY e.paid_by
        """
        cursor.execute(receivable_sql, (group_id,))
        for row in cursor.fetchall():
            pid = row['paid_by']
            if pid in balances:
                balances[pid]['receivable'] = round(row['total_receivable'], 2)
                
        # 2. 計算每個人的應付 (即別人付的款，此人需要分攤且未結清的部分)
        payable_sql = """
            SELECT s.user_id, SUM(s.amount) as total_payable
            FROM expense_splits s
            JOIN expenses e ON s.expense_id = e.id
            WHERE e.group_id = ? AND s.is_settled = 0 AND s.user_id != e.paid_by
            GROUP BY s.user_id
        """
        cursor.execute(payable_sql, (group_id,))
        for row in cursor.fetchall():
            uid = row['user_id']
            if uid in balances:
                balances[uid]['payable'] = round(row['total_payable'], 2)
                
        # 3. 計算淨額
        for uid in balances:
            balances[uid]['net'] = round(balances[uid]['receivable'] - balances[uid]['payable'], 2)
            
        return balances
    except sqlite3.Error as e:
        logging.error(f"Error calculating group balances: {e}")
        return {}
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
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
                data.get('group_id'),
                data.get('title'),
                data.get('amount'),
                data.get('category'),
                data.get('paid_by')
<<<<<<< HEAD
            ))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Error in create expense: {e}")
        return None

def get_all():
    """
    取得所有開支記錄
    :return: list of Row
    """
    sql = "SELECT * FROM expenses"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_all expenses: {e}")
        return []

def get_by_group_id(group_id):
    """
    取得某個群組的所有開支記錄，並按時間由新到舊排序
    :param group_id: int, 群組 ID
    :return: list of Row
    """
    sql = "SELECT * FROM expenses WHERE group_id = ? ORDER BY created_at DESC"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (group_id,)).fetchall()
    except sqlite3.Error as e:
        print(f"Error in get_by_group_id expenses ({group_id}): {e}")
        return []

def get_by_id(expense_id):
    """
    依 ID 取得單筆開支記錄
    :param expense_id: int, 開支 ID
    :return: Row 或 None
    """
    sql = "SELECT * FROM expenses WHERE id = ?"
    try:
        with get_db_connection() as conn:
            return conn.execute(sql, (expense_id,)).fetchone()
    except sqlite3.Error as e:
        print(f"Error in get_by_id expense ({expense_id}): {e}")
        return None

def update(expense_id, data):
    """
    更新開支資料
    :param expense_id: int, 開支 ID
    :param data: dict, 需要更新的欄位值
    :return: bool 是否更新成功
    """
    if not data:
        return False
        
    keys = list(data.keys())
    set_clause = ", ".join([f"{key} = ?" for key in keys])
    sql = f"UPDATE expenses SET {set_clause} WHERE id = ?"
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            params = [data[key] for key in keys]
            params.append(expense_id)
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in update expense ({expense_id}): {e}")
        return False

def delete(expense_id):
    """
    刪除開支記錄
    :param expense_id: int, 開支 ID
    :return: bool 是否刪除成功
    """
    sql = "DELETE FROM expenses WHERE id = ?"
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (expense_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error in delete expense ({expense_id}): {e}")
        return False
=======
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

>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
