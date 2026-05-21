from app.models import get_db_connection

class ElectricitySplit:
    """ElectricitySplit Model — 電費分攤"""
    def __init__(self, row):
        self.id = row['id']
        self.bill_id = row['bill_id']
        self.user_id = row['user_id']
        self.personal_amount = row['personal_amount']
        self.shared_amount = row['shared_amount']
        self.total_amount = row['total_amount']
        self.is_paid = row['is_paid']

    def __getitem__(self, key):
        return getattr(self, key)

    @classmethod
    def create(cls, data):
        """新增分攤結果"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO electricity_splits (bill_id, user_id, personal_amount, shared_amount, total_amount, is_paid) VALUES (?, ?, ?, ?, ?, ?)",
                (data.get('bill_id'), data.get('user_id'), data.get('personal_amount'), data.get('shared_amount'), data.get('total_amount'), data.get('is_paid', 0))
            )
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return cls.get_by_id(new_id)
        except Exception as e:
            print(f"Error creating electricity split: {e}")
            return None

    @classmethod
    def get_all(cls):
        """取得所有分攤結果"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM electricity_splits").fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting all electricity splits: {e}")
            return []

    @classmethod
    def get_by_id(cls, split_id):
        """依 ID 取得分攤結果"""
        try:
            conn = get_db_connection()
            row = conn.execute("SELECT * FROM electricity_splits WHERE id = ?", (split_id,)).fetchone()
            conn.close()
            return cls(row) if row else None
        except Exception as e:
            print(f"Error getting electricity split by id: {e}")
            return None

    @classmethod
    def get_by_bill(cls, bill_id):
        """取得特定帳單的所有分攤結果"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM electricity_splits WHERE bill_id = ?", (bill_id,)).fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting splits by bill: {e}")
            return []

    @classmethod
    def update(cls, split_id, data):
        """更新分攤結果"""
        try:
            conn = get_db_connection()
            fields = []
            values = []
            for key, val in data.items():
                fields.append(f"{key} = ?")
                values.append(val)
            values.append(split_id)
            query = f"UPDATE electricity_splits SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, tuple(values))
            conn.commit()
            conn.close()
            return cls.get_by_id(split_id)
        except Exception as e:
            print(f"Error updating electricity split: {e}")
            return None

    @classmethod
    def delete(cls, split_id):
        """刪除分攤結果"""
        try:
            conn = get_db_connection()
            conn.execute("DELETE FROM electricity_splits WHERE id = ?", (split_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting electricity split: {e}")
            return False
