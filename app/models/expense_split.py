from app.models import get_db_connection

class ExpenseSplit:
    """ExpenseSplit Model — 開支分攤"""
    def __init__(self, row):
        self.id = row['id']
        self.expense_id = row['expense_id']
        self.user_id = row['user_id']
        self.amount = row['amount']
        self.is_settled = row['is_settled']

    def __getitem__(self, key):
        return getattr(self, key)

    @classmethod
    def create(cls, data):
        """建立分攤記錄"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO expense_splits (expense_id, user_id, amount, is_settled) VALUES (?, ?, ?, ?)",
                (data.get('expense_id'), data.get('user_id'), data.get('amount'), data.get('is_settled', 0))
            )
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return cls.get_by_id(new_id)
        except Exception as e:
            print(f"Error creating expense split: {e}")
            return None

    @classmethod
    def get_all(cls):
        """取得所有分攤記錄"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM expense_splits").fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting all expense splits: {e}")
            return []

    @classmethod
    def get_by_id(cls, split_id):
        """依 ID 取得分攤記錄"""
        try:
            conn = get_db_connection()
            row = conn.execute("SELECT * FROM expense_splits WHERE id = ?", (split_id,)).fetchone()
            conn.close()
            return cls(row) if row else None
        except Exception as e:
            print(f"Error getting expense split by id: {e}")
            return None

    @classmethod
    def get_by_expense(cls, expense_id):
        """取得特定消費項目的所有分攤記錄"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM expense_splits WHERE expense_id = ?", (expense_id,)).fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting splits by expense: {e}")
            return []

    @classmethod
    def get_by_user(cls, user_id):
        """取得特定使用者的所有分攤記錄"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM expense_splits WHERE user_id = ?", (user_id,)).fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting splits by user: {e}")
            return []

    @classmethod
    def settle_splits(cls, user1_id, user2_id):
        """結算雙方的未結清開支：將 user1_id 幫 user2_id 付的，及 user2_id 幫 user1_id 付的皆標記為已結清"""
        try:
            conn = get_db_connection()
            # 結算 user1 支付、user2 應分攤的
            conn.execute(
                "UPDATE expense_splits SET is_settled = 1 WHERE user_id = ? AND is_settled = 0 AND expense_id IN (SELECT id FROM expenses WHERE paid_by = ?)",
                (user2_id, user1_id)
            )
            # 結算 user2 支付、user1 應分攤的
            conn.execute(
                "UPDATE expense_splits SET is_settled = 1 WHERE user_id = ? AND is_settled = 0 AND expense_id IN (SELECT id FROM expenses WHERE paid_by = ?)",
                (user1_id, user2_id)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error settling splits: {e}")
            return False

    @classmethod
    def update(cls, split_id, data):
        """更新分攤記錄"""
        try:
            conn = get_db_connection()
            fields = []
            values = []
            for key, val in data.items():
                fields.append(f"{key} = ?")
                values.append(val)
            values.append(split_id)
            query = f"UPDATE expense_splits SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, tuple(values))
            conn.commit()
            conn.close()
            return cls.get_by_id(split_id)
        except Exception as e:
            print(f"Error updating expense split: {e}")
            return None

    @classmethod
    def delete(cls, split_id):
        """刪除分攤記錄"""
        try:
            conn = get_db_connection()
            conn.execute("DELETE FROM expense_splits WHERE id = ?", (split_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting expense split: {e}")
            return False
