from app.models import get_db_connection

class Agreement:
    """Agreement Model — 室友公約"""
    def __init__(self, row):
        self.id = row['id']
        self.group_id = row['group_id']
        self.title = row['title']
        self.category = row['category']
        self.content = row['content']
        self.status = row['status']
        self.created_by = row['created_by']
        self.created_at = row['created_at']
        self.updated_at = row['updated_at']

    def __getitem__(self, key):
        return getattr(self, key)

    @classmethod
    def create(cls, data):
        """新增一筆公約"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO agreements (group_id, title, category, content, status, created_by) VALUES (?, ?, ?, ?, ?, ?)",
                (data.get('group_id'), data.get('title'), data.get('category'), data.get('content'), data.get('status', 'pending'), data.get('created_by'))
            )
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return cls.get_by_id(new_id)
        except Exception as e:
            print(f"Error creating agreement: {e}")
            return None

    @classmethod
    def get_all(cls):
        """取得所有公約"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM agreements").fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting all agreements: {e}")
            return []

    @classmethod
    def get_by_id(cls, agreement_id):
        """依 ID 取得公約"""
        try:
            conn = get_db_connection()
            row = conn.execute("SELECT * FROM agreements WHERE id = ?", (agreement_id,)).fetchone()
            conn.close()
            return cls(row) if row else None
        except Exception as e:
            print(f"Error getting agreement by id: {e}")
            return None

    @classmethod
    def get_by_group(cls, group_id):
        """取得特定群組的所有公約"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM agreements WHERE group_id = ?", (group_id,)).fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting agreements by group: {e}")
            return []

    @classmethod
    def update(cls, agreement_id, data):
        """更新公約"""
        try:
            conn = get_db_connection()
            fields = []
            values = []
            for key, val in data.items():
                fields.append(f"{key} = ?")
                values.append(val)
            fields.append("updated_at = CURRENT_TIMESTAMP")
            values.append(agreement_id)
            query = f"UPDATE agreements SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, tuple(values))
            conn.commit()
            conn.close()
            return cls.get_by_id(agreement_id)
        except Exception as e:
            print(f"Error updating agreement: {e}")
            return None

    @classmethod
    def delete(cls, agreement_id):
        """刪除公約"""
        try:
            conn = get_db_connection()
            conn.execute("DELETE FROM agreements WHERE id = ?", (agreement_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting agreement: {e}")
            return False
