from app.models import get_db_connection

class Expense:
    """Expense Model — 共同開支"""
    def __init__(self, row):
        self.id = row['id']
        self.group_id = row['group_id']
        self.title = row['title']
        self.amount = row['amount']
        self.category = row['category']
        self.paid_by = row['paid_by']
        self.created_at = row['created_at']

    def __getitem__(self, key):
        return getattr(self, key)

    @classmethod
    def create(cls, data):
        """新增一筆消費記帳"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO expenses (group_id, title, amount, category, paid_by) VALUES (?, ?, ?, ?, ?)",
                (data.get('group_id'), data.get('title'), data.get('amount'), data.get('category'), data.get('paid_by'))
            )
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return cls.get_by_id(new_id)
        except Exception as e:
            print(f"Error creating expense: {e}")
            return None

    @classmethod
    def get_all(cls):
        """取得所有記帳記錄"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM expenses").fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting all expenses: {e}")
            return []

    @classmethod
    def get_by_id(cls, expense_id):
        """依 ID 取得記帳記錄"""
        try:
            conn = get_db_connection()
            row = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
            conn.close()
            return cls(row) if row else None
        except Exception as e:
            print(f"Error getting expense by id: {e}")
            return None

    @classmethod
    def get_by_group(cls, group_id):
        """取得特定群組的所有消費記錄，依記帳時間降冪排列"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM expenses WHERE group_id = ? ORDER BY created_at DESC", (group_id,)).fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting expenses by group: {e}")
            return []

    @classmethod
    def update(cls, expense_id, data):
        """更新消費記錄"""
        try:
            conn = get_db_connection()
            fields = []
            values = []
            for key, val in data.items():
                fields.append(f"{key} = ?")
                values.append(val)
            values.append(expense_id)
            query = f"UPDATE expenses SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, tuple(values))
            conn.commit()
            conn.close()
            return cls.get_by_id(expense_id)
        except Exception as e:
            print(f"Error updating expense: {e}")
            return None

    @classmethod
    def delete(cls, expense_id):
        """刪除消費記錄"""
        try:
            conn = get_db_connection()
            conn.execute("DELETE FROM expense_splits WHERE expense_id = ?", (expense_id,))
            conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting expense: {e}")
            return False
