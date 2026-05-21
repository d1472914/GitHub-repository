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
