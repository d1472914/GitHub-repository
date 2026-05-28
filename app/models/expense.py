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
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
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
                data.get('group_id'),
                data.get('title'),
                data.get('amount'),
                data.get('category'),
                data.get('paid_by')
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
