from app.models import get_db_connection

class Chore:
    """Chore Model — 家事任務"""
    def __init__(self, row):
        self.id = row['id']
        self.group_id = row['group_id']
        self.title = row['title']
        self.description = row['description']
        self.recurrence = row['recurrence']
        self.due_date = row['due_date']
        self.assigned_to = row['assigned_to']
        self.status = row['status']
        self.created_by = row['created_by']
        self.completed_at = row['completed_at']
        self.created_at = row['created_at']

    def __getitem__(self, key):
        return getattr(self, key)

    @classmethod
    def create(cls, data):
        """建立排班任務"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO chores (group_id, title, description, recurrence, due_date, assigned_to, status, created_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (data.get('group_id'), data.get('title'), data.get('description'), data.get('recurrence', 'once'), data.get('due_date'), data.get('assigned_to'), data.get('status', 'pending'), data.get('created_by'))
            )
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return cls.get_by_id(new_id)
        except Exception as e:
            print(f"Error creating chore: {e}")
            return None

    @classmethod
    def get_all(cls):
        """取得所有任務記錄"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM chores").fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting all chores: {e}")
            return []

    @classmethod
    def get_by_id(cls, chore_id):
        """依 ID 取得任務記錄"""
        try:
            conn = get_db_connection()
            row = conn.execute("SELECT * FROM chores WHERE id = ?", (chore_id,)).fetchone()
            conn.close()
            return cls(row) if row else None
        except Exception as e:
            print(f"Error getting chore by id: {e}")
            return None

    @classmethod
    def get_by_group(cls, group_id):
        """取得特定群組的所有任務，依到期日升冪排列"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM chores WHERE group_id = ? ORDER BY due_date ASC", (group_id,)).fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting chores by group: {e}")
            return []

    @classmethod
    def get_pending_by_user(cls, user_id):
        """取得特定使用者的所有待完成任務"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM chores WHERE assigned_to = ? AND status = 'pending' ORDER BY due_date ASC", (user_id,)).fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting pending chores by user: {e}")
            return []

    @classmethod
    def update(cls, chore_id, data):
        """更新任務記錄"""
        try:
            conn = get_db_connection()
            fields = []
            values = []
            for key, val in data.items():
                fields.append(f"{key} = ?")
                values.append(val)
            values.append(chore_id)
            query = f"UPDATE chores SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, tuple(values))
            conn.commit()
            conn.close()
            return cls.get_by_id(chore_id)
        except Exception as e:
            print(f"Error updating chore: {e}")
            return None

    @classmethod
    def delete(cls, chore_id):
        """刪除任務"""
        try:
            conn = get_db_connection()
            conn.execute("DELETE FROM chores WHERE id = ?", (chore_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting chore: {e}")
            return False
