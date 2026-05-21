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
    建立一個新的物資品項。
    
    Args:
        data (dict): 包含 group_id, name, unit, quantity, min_quantity, created_by 的字典。
        
    Returns:
        int: 新增物資的 id，若失敗則回傳 None。
    """
    sql = """
        INSERT INTO inventory_items (group_id, name, unit, quantity, min_quantity, created_by)
        VALUES (:group_id, :name, :unit, :quantity, :min_quantity, :created_by)
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        params = {
            'group_id': data.get('group_id'),
            'name': data.get('name'),
            'unit': data.get('unit'),
            'quantity': data.get('quantity', 0),
            'min_quantity': data.get('min_quantity', 0),
            'created_by': data.get('created_by')
        }
        
        cursor.execute(sql, params)
        item_id = cursor.lastrowid
        
        # 若初始庫存量大於 0，自動新增一筆 stock_in 日誌
        initial_qty = params['quantity']
        if initial_qty > 0:
            log_sql = """
                INSERT INTO inventory_logs (item_id, user_id, action, quantity, note)
                VALUES (?, ?, 'stock_in', ?, '初始庫存建立')
            """
            cursor.execute(log_sql, (item_id, params['created_by'], initial_qty))
            
        conn.commit()
        return item_id
    except sqlite3.Error as e:
        logging.error(f"Error creating inventory item: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def get_all():
    """
    取得所有物資品項。
    
    Returns:
        list: 所有物資品項列表。
    """
    sql = "SELECT * FROM inventory_items"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error getting all inventory items: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_by_id(item_id):
    """
    取得單筆物資品項。
    
    Args:
        item_id (int): 物資 ID。
        
    Returns:
        sqlite3.Row: 物資記錄。
    """
    sql = "SELECT * FROM inventory_items WHERE id = ?"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (item_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        logging.error(f"Error getting inventory item by id: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_by_group(group_id):
    """
    取得群組的所有物資品項。
    
    Args:
        group_id (int): 群組 ID。
        
    Returns:
        list: 物資記錄列表。
    """
    sql = "SELECT * FROM inventory_items WHERE group_id = ? ORDER BY name ASC"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (group_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error getting inventory items by group: {e}")
        return []
    finally:
        if conn:
            conn.close()

def update(item_id, data):
    """
    更新物資資訊（例如名稱、單位、最低庫存限制）。
    注意：這不應該直接用來調整庫存數量，調整數量請使用 `log_transaction`。
    
    Args:
        item_id (int): 物資 ID。
        data (dict): 更新的欄位與值（如 name, unit, min_quantity）。
        
    Returns:
        bool: 是否更新成功。
    """
    if not data:
        return False
        
    fields = ["updated_at = CURRENT_TIMESTAMP"]
    params = {'id': item_id}
    for key in ['name', 'unit', 'min_quantity']:
        if key in data:
            fields.append(f"{key} = :{key}")
            params[key] = data[key]
            
    if len(fields) == 1:
        return False
        
    sql = f"UPDATE inventory_items SET {', '.join(fields)} WHERE id = :id"
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error updating inventory item: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def delete(item_id):
    """
    刪除物資品項，並自動刪除關聯的操作日誌。
    
    Args:
        item_id (int): 物資 ID。
        
    Returns:
        bool: 是否刪除成功。
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM inventory_logs WHERE item_id = ?", (item_id,))
        cursor.execute("DELETE FROM inventory_items WHERE id = ?", (item_id,))
        
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Error deleting inventory item: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

# --- 額外輔助功能：入庫/出庫日誌與庫存更新交易 ---

def log_transaction(data):
    """
    記錄一次入庫或出庫操作，並在同一個 transaction 中更新庫存量。
    
    Args:
        data (dict): 包含 item_id, user_id, action ('stock_in' 或 'stock_out'), quantity, note 的字典。
        
    Returns:
        int: 交易日誌 id，若失敗或庫存不足則回傳 None。
    """
    item_id = data.get('item_id')
    user_id = data.get('user_id')
    action = data.get('action')
    qty = int(data.get('quantity', 0))
    note = data.get('note', '')
    
    if qty <= 0:
        return None
        
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. 取得目前庫存量與商品資訊
        cursor.execute("SELECT quantity, name FROM inventory_items WHERE id = ?", (item_id,))
        item = cursor.fetchone()
        if not item:
            logging.error(f"Inventory item {item_id} not found.")
            return None
            
        current_qty = item['quantity']
        new_qty = current_qty
        
        # 2. 計算新庫存量並做基本驗證
        if action == 'stock_in':
            new_qty = current_qty + qty
        elif action == 'stock_out':
            if current_qty < qty:
                logging.error(f"Insufficient stock for {item['name']}. Current: {current_qty}, Requested: {qty}")
                return None # 庫存不足，不允許出庫
            new_qty = current_qty - qty
        else:
            logging.error(f"Invalid action type: {action}")
            return None
            
        # 3. 寫入 inventory_logs
        log_sql = """
            INSERT INTO inventory_logs (item_id, user_id, action, quantity, note)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor.execute(log_sql, (item_id, user_id, action, qty, note))
        log_id = cursor.lastrowid
        
        # 4. 更新 inventory_items 的庫存量與更新時間
        update_item_sql = """
            UPDATE inventory_items 
            SET quantity = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """
        cursor.execute(update_item_sql, (new_qty, item_id))
        
        conn.commit()
        return log_id
    except sqlite3.Error as e:
        logging.error(f"Error logging inventory transaction: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def get_logs(item_id):
    """
    取得特定物資品項的入出庫歷史操作記錄，包含操作者暱稱。
    
    Args:
        item_id (int): 物資 ID。
        
    Returns:
        list: 操作記錄列表。
    """
    sql = """
        SELECT l.*, u.nickname 
        FROM inventory_logs l
        JOIN users u ON l.user_id = u.id
        WHERE l.item_id = ?
        ORDER BY l.created_at DESC, l.id DESC
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, (item_id,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error getting inventory logs: {e}")
        return []
    finally:
        if conn:
            conn.close()

