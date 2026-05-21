from app.models import get_db_connection

class InventoryLog:
    """InventoryLog Model — 物資異動日誌"""
    def __init__(self, row):
        self.id = row['id']
        self.item_id = row['item_id']
        self.user_id = row['user_id']
        self.action = row['action']
        self.quantity = row['quantity']
        self.note = row['note']
        self.created_at = row['created_at']
        # 關聯屬性 (選用，可在與 User/Item 關聯查詢時儲存)
        self.user_nickname = row.get('nickname') if 'nickname' in row.keys() else None
        self.item_name = row.get('item_name') if 'item_name' in row.keys() else None

    def __getitem__(self, key):
        return getattr(self, key)

    @classmethod
    def create(cls, data):
        """新增一筆物資異動記錄"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO inventory_logs (item_id, user_id, action, quantity, note, created_at) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
                (data.get('item_id'), data.get('user_id'), data.get('action'), data.get('quantity'), data.get('note'))
            )
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return cls.get_by_id(new_id)
        except Exception as e:
            print(f"Error creating inventory log: {e}")
            return None

    @classmethod
    def get_all(cls):
        """取得所有物資異動記錄"""
        try:
            conn = get_db_connection()
            rows = conn.execute(
                "SELECT l.*, u.nickname, i.name as item_name FROM inventory_logs l "
                "LEFT JOIN users u ON l.user_id = u.id "
                "LEFT JOIN inventory_items i ON l.item_id = i.id "
                "ORDER BY l.created_at DESC"
            ).fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting all inventory logs: {e}")
            return []

    @classmethod
    def get_by_id(cls, log_id):
        """依 ID 取得單筆物資異動記錄"""
        try:
            conn = get_db_connection()
            row = conn.execute(
                "SELECT l.*, u.nickname, i.name as item_name FROM inventory_logs l "
                "LEFT JOIN users u ON l.user_id = u.id "
                "LEFT JOIN inventory_items i ON l.item_id = i.id "
                "WHERE l.id = ?", (log_id,)
            ).fetchone()
            conn.close()
            return cls(row) if row else None
        except Exception as e:
            print(f"Error getting inventory log by id: {e}")
            return None

    @classmethod
    def get_by_item(cls, item_id):
        """取得特定物資品項的異動記錄，依時間降冪排列"""
        try:
            conn = get_db_connection()
            rows = conn.execute(
                "SELECT l.*, u.nickname, i.name as item_name FROM inventory_logs l "
                "LEFT JOIN users u ON l.user_id = u.id "
                "LEFT JOIN inventory_items i ON l.item_id = i.id "
                "WHERE l.item_id = ? ORDER BY l.created_at DESC", (item_id,)
            ).fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting inventory logs by item: {e}")
            return []

    @classmethod
    def update(cls, log_id, data):
        """更新物資異動記錄 (雖然日誌通常不更新，但配合 CRUD 規範提供)"""
        try:
            conn = get_db_connection()
            fields = []
            values = []
            for key, val in data.items():
                fields.append(f"{key} = ?")
                values.append(val)
            values.append(log_id)
            query = f"UPDATE inventory_logs SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, tuple(values))
            conn.commit()
            conn.close()
            return cls.get_by_id(log_id)
        except Exception as e:
            print(f"Error updating inventory log: {e}")
            return None

    @classmethod
    def delete(cls, log_id):
        """刪除物資異動記錄"""
        try:
            conn = get_db_connection()
            conn.execute("DELETE FROM inventory_logs WHERE id = ?", (log_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting inventory log: {e}")
            return False
