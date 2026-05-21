from app.models import get_db_connection

class Notification:
    """Notification Model — 通知"""
    def __init__(self, row):
        self.id = row['id']
        self.user_id = row['user_id']
        self.group_id = row['group_id']
        self.type = row['type']
        self.title = row['title']
        self.message = row['message']
        self.is_read = bool(row['is_read'])
        self.created_at = row['created_at']

    def __getitem__(self, key):
        return getattr(self, key)

    @classmethod
    def create(cls, data):
        """新增一筆通知"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notifications (user_id, group_id, type, title, message, is_read, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
                (data.get('user_id'), data.get('group_id'), data.get('type'), data.get('title'), data.get('message'), data.get('is_read', 0))
            )
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return cls.get_by_id(new_id)
        except Exception as e:
            print(f"Error creating notification: {e}")
            return None

    @classmethod
    def get_all(cls):
        """取得所有通知"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM notifications ORDER BY created_at DESC").fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting all notifications: {e}")
            return []

    @classmethod
    def get_by_id(cls, notif_id):
        """依 ID 取得單筆通知"""
        try:
            conn = get_db_connection()
            row = conn.execute("SELECT * FROM notifications WHERE id = ?", (notif_id,)).fetchone()
            conn.close()
            return cls(row) if row else None
        except Exception as e:
            print(f"Error getting notification by id: {e}")
            return None

    @classmethod
    def get_unread_by_user(cls, user_id):
        """取得特定使用者的未讀通知"""
        try:
            conn = get_db_connection()
            rows = conn.execute(
                "SELECT * FROM notifications WHERE user_id = ? AND is_read = 0 ORDER BY created_at DESC", 
                (user_id,)
            ).fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting unread notifications: {e}")
            return []

    @classmethod
    def get_by_user(cls, user_id):
        """取得特定使用者的所有通知 (讀取+未讀)，依時間降冪"""
        try:
            conn = get_db_connection()
            rows = conn.execute(
                "SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC", 
                (user_id,)
            ).fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting notifications by user: {e}")
            return []

    @classmethod
    def update(cls, notif_id, data):
        """更新通知"""
        try:
            conn = get_db_connection()
            fields = []
            values = []
            for key, val in data.items():
                fields.append(f"{key} = ?")
                # 確保布林值轉為整數
                if key == 'is_read':
                    values.append(1 if val else 0)
                else:
                    values.append(val)
            values.append(notif_id)
            query = f"UPDATE notifications SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, tuple(values))
            conn.commit()
            conn.close()
            return cls.get_by_id(notif_id)
        except Exception as e:
            print(f"Error updating notification: {e}")
            return None

    @classmethod
    def mark_as_read(cls, notif_id):
        """標記單筆通知為已讀"""
        return cls.update(notif_id, {'is_read': True})

    @classmethod
    def mark_all_as_read(cls, user_id):
        """將特定使用者的所有通知標記為已讀"""
        try:
            conn = get_db_connection()
            conn.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error marking all notifications as read: {e}")
            return False

    @classmethod
    def delete(cls, notif_id):
        """刪除通知"""
        try:
            conn = get_db_connection()
            conn.execute("DELETE FROM notifications WHERE id = ?", (notif_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting notification: {e}")
            return False
