from app.models import get_db_connection

class Group:
    """Group Model — 群組"""
    def __init__(self, row):
        self.id = row['id']
        self.name = row['name']
        self.invite_code = row['invite_code']
        self.created_by = row['created_by']
        self.created_at = row['created_at']

    def __getitem__(self, key):
        return getattr(self, key)

    @classmethod
    def create(cls, data):
        """建立新群組"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO groups (name, invite_code, created_by) VALUES (?, ?, ?)",
                (data.get('name'), data.get('invite_code'), data.get('created_by'))
            )
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return cls.get_by_id(new_id)
        except Exception as e:
            print(f"Error creating group: {e}")
            return None

    @classmethod
    def get_all(cls):
        """取得所有群組"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM groups").fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting all groups: {e}")
            return []

    @classmethod
    def get_by_id(cls, group_id):
        """依 ID 取得群組"""
        try:
            conn = get_db_connection()
            row = conn.execute("SELECT * FROM groups WHERE id = ?", (group_id,)).fetchone()
            conn.close()
            return cls(row) if row else None
        except Exception as e:
            print(f"Error getting group by id: {e}")
            return None

    @classmethod
    def get_by_invite_code(cls, invite_code):
        """依邀請碼取得群組"""
        try:
            conn = get_db_connection()
            row = conn.execute("SELECT * FROM groups WHERE invite_code = ?", (invite_code,)).fetchone()
            conn.close()
            return cls(row) if row else None
        except Exception as e:
            print(f"Error getting group by invite code: {e}")
            return None

    @classmethod
    def update(cls, group_id, data):
        """更新群組資訊"""
        try:
            conn = get_db_connection()
            fields = []
            values = []
            for key, val in data.items():
                fields.append(f"{key} = ?")
                values.append(val)
            values.append(group_id)
            query = f"UPDATE groups SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, tuple(values))
            conn.commit()
            conn.close()
            return cls.get_by_id(group_id)
        except Exception as e:
            print(f"Error updating group: {e}")
            return None

    @classmethod
    def delete(cls, group_id):
        """刪除群組"""
        try:
            conn = get_db_connection()
            conn.execute("DELETE FROM groups WHERE id = ?", (group_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting group: {e}")
            return False
