from flask_login import UserMixin
from app.models import get_db_connection

class User(UserMixin):
    """User Model — 使用者"""
    def __init__(self, row):
        self.id = row['id']
        self.email = row['email']
        self.password_hash = row['password_hash']
        self.nickname = row['nickname']
        self.role = row['role']
        self.group_id = row['group_id']
        self.created_at = row['created_at']

    def __getitem__(self, key):
        return getattr(self, key)

    @classmethod
    def create(cls, data):
        """新增一筆使用者記錄"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (email, password_hash, nickname, role, group_id) VALUES (?, ?, ?, ?, ?)",
                (data.get('email'), data.get('password_hash'), data.get('nickname'), data.get('role', 'member'), data.get('group_id'))
            )
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return cls.get_by_id(new_id)
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    @classmethod
    def get_all(cls):
        """取得所有使用者記錄"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM users").fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []

    @classmethod
    def get_by_id(cls, user_id):
        """取得單筆使用者記錄 (依 ID)"""
        try:
            conn = get_db_connection()
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            conn.close()
            return cls(row) if row else None
        except Exception as e:
            print(f"Error getting user by id: {e}")
            return None

    @classmethod
    def get_by_email(cls, email):
        """取得單筆使用者記錄 (依 Email)"""
        try:
            conn = get_db_connection()
            row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            conn.close()
            return cls(row) if row else None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None

    @classmethod
    def get_by_group(cls, group_id):
        """取得特定群組的所有成員"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM users WHERE group_id = ?", (group_id,)).fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting users by group: {e}")
            return []

    @classmethod
    def update(cls, user_id, data):
        """更新使用者記錄"""
        try:
            conn = get_db_connection()
            fields = []
            values = []
            for key, val in data.items():
                fields.append(f"{key} = ?")
                values.append(val)
            values.append(user_id)
            query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, tuple(values))
            conn.commit()
            conn.close()
            return cls.get_by_id(user_id)
        except Exception as e:
            print(f"Error updating user: {e}")
            return None

    @classmethod
    def delete(cls, user_id):
        """刪除使用者記錄"""
        try:
            conn = get_db_connection()
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
