from app.models import get_db_connection

class ElectricityBill:
    """ElectricityBill Model — 電費帳單"""
    def __init__(self, row):
        self.id = row['id']
        self.group_id = row['group_id']
        self.total_amount = row['total_amount']
        self.total_kwh = row['total_kwh']
        self.period_start = row['period_start']
        self.period_end = row['period_end']
        self.created_by = row['created_by']
        self.created_at = row['created_at']

    def __getitem__(self, key):
        return getattr(self, key)

    @classmethod
    def create(cls, data):
        """新增一筆電費帳單記錄"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO electricity_bills (group_id, total_amount, total_kwh, period_start, period_end, created_by) VALUES (?, ?, ?, ?, ?, ?)",
                (data.get('group_id'), data.get('total_amount'), data.get('total_kwh'), data.get('period_start'), data.get('period_end'), data.get('created_by'))
            )
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return cls.get_by_id(new_id)
        except Exception as e:
            print(f"Error creating electricity bill: {e}")
            return None

    @classmethod
    def get_all(cls):
        """取得所有電費帳單"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM electricity_bills").fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting all electricity bills: {e}")
            return []

    @classmethod
    def get_by_id(cls, bill_id):
        """依 ID 取得電費帳單"""
        try:
            conn = get_db_connection()
            row = conn.execute("SELECT * FROM electricity_bills WHERE id = ?", (bill_id,)).fetchone()
            conn.close()
            return cls(row) if row else None
        except Exception as e:
            print(f"Error getting electricity bill by id: {e}")
            return None

    @classmethod
    def get_by_group(cls, group_id):
        """取得特定群組的所有電費帳單，依計費起始日降冪排列"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM electricity_bills WHERE group_id = ? ORDER BY period_start DESC", (group_id,)).fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting bills by group: {e}")
            return []

    @classmethod
    def update(cls, bill_id, data):
        """更新電費帳單"""
        try:
            conn = get_db_connection()
            fields = []
            values = []
            for key, val in data.items():
                fields.append(f"{key} = ?")
                values.append(val)
            values.append(bill_id)
            query = f"UPDATE electricity_bills SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, tuple(values))
            conn.commit()
            conn.close()
            return cls.get_by_id(bill_id)
        except Exception as e:
            print(f"Error updating electricity bill: {e}")
            return None

    @classmethod
    def delete(cls, bill_id):
        """刪除電費帳單 (同時刪除對應的度數登錄與分攤結果)"""
        try:
            conn = get_db_connection()
            conn.execute("DELETE FROM electricity_splits WHERE bill_id = ?", (bill_id,))
            conn.execute("DELETE FROM meter_readings WHERE bill_id = ?", (bill_id,))
            conn.execute("DELETE FROM electricity_bills WHERE id = ?", (bill_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting electricity bill: {e}")
            return False
