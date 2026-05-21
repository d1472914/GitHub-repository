from app.models import get_db_connection

class InventoryItem:
    """InventoryItem Model — 共同物資品項"""
    def __init__(self, row):
        self.id = row['id']
        self.group_id = row['group_id']
        self.name = row['name']
        self.unit = row['unit']
        self.quantity = row['quantity']
        self.min_quantity = row['min_quantity']
        self.created_by = row['created_by']
        self.created_at = row['created_at']
        self.updated_at = row['updated_at']

    def __getitem__(self, key):
        return getattr(self, key)

    @property
    def is_low_stock(self):
        """檢查是否低於最低庫存量"""
        return self.quantity < self.min_quantity

    def stock_in(self, qty):
        """登記增加庫存 (入庫)"""
        try:
            conn = get_db_connection()
            conn.execute(
                "UPDATE inventory_items SET quantity = quantity + ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (qty, self.id)
            )
            conn.commit()
            conn.close()
            self.quantity += qty
            return True
        except Exception as e:
            print(f"Error during stock_in: {e}")
            return False

    def stock_out(self, qty):
        """登記減少庫存 (出庫)"""
        try:
            conn = get_db_connection()
            conn.execute(
                "UPDATE inventory_items SET quantity = quantity - ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (qty, self.id)
            )
            conn.commit()
            conn.close()
            self.quantity -= qty
            return True
        except Exception as e:
            print(f"Error during stock_out: {e}")
            return False

    @classmethod
    def create(cls, data):
        """新增一個物資品項"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO inventory_items (group_id, name, unit, quantity, min_quantity, created_by) VALUES (?, ?, ?, ?, ?, ?)",
                (data.get('group_id'), data.get('name'), data.get('unit'), data.get('quantity', 0), data.get('min_quantity', 0), data.get('created_by'))
            )
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return cls.get_by_id(new_id)
        except Exception as e:
            print(f"Error creating inventory item: {e}")
            return None

    @classmethod
    def get_all(cls):
        """取得所有物資品項"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM inventory_items").fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting all inventory items: {e}")
            return []

    @classmethod
    def get_by_id(cls, item_id):
        """依 ID 取得物資品項"""
        try:
            conn = get_db_connection()
            row = conn.execute("SELECT * FROM inventory_items WHERE id = ?", (item_id,)).fetchone()
            conn.close()
            return cls(row) if row else None
        except Exception as e:
            print(f"Error getting inventory item by id: {e}")
            return None

    @classmethod
    def get_by_group(cls, group_id):
        """取得特定群組的所有物資品項，依最後更新時間降冪排列"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM inventory_items WHERE group_id = ? ORDER BY updated_at DESC", (group_id,)).fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting inventory items by group: {e}")
            return []

    @classmethod
    def update(cls, item_id, data):
        """更新物資品項屬性"""
        try:
            conn = get_db_connection()
            fields = []
            values = []
            for key, val in data.items():
                fields.append(f"{key} = ?")
                values.append(val)
            fields.append("updated_at = CURRENT_TIMESTAMP")
            values.append(item_id)
            query = f"UPDATE inventory_items SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, tuple(values))
            conn.commit()
            conn.close()
            return cls.get_by_id(item_id)
        except Exception as e:
            print(f"Error updating inventory item: {e}")
            return None

    @classmethod
    def delete(cls, item_id):
        """刪除物資品項"""
        try:
            conn = get_db_connection()
            conn.execute("DELETE FROM inventory_logs WHERE item_id = ?", (item_id,))
            conn.execute("DELETE FROM inventory_items WHERE id = ?", (item_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting inventory item: {e}")
            return False
