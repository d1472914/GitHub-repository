from app.models import get_db_connection

class Reminder:
    """Reminder Model — 匿名提醒"""
    def __init__(self, row):
        self.id = row['id']
        self.group_id = row['group_id']
        self.receiver_id = row['receiver_id']
        self.category = row['category']
        self.message = row['message']
        self.created_at = row['created_at']
        # sender_id 可能為空 (在收件匣中不向接收者洩露發送者)
        try:
            self.sender_id = row['sender_id']
        except (IndexError, KeyError):
            self.sender_id = None

    def __getitem__(self, key):
        return getattr(self, key)

    @classmethod
    def create(cls, data):
        """建立匿名提醒"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO reminders (group_id, sender_id, receiver_id, category, message) VALUES (?, ?, ?, ?, ?)",
                (data.get('group_id'), data.get('sender_id'), data.get('receiver_id'), data.get('category'), data.get('message'))
            )
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return cls.get_by_id(new_id)
        except Exception as e:
            print(f"Error creating reminder: {e}")
            return None

    @classmethod
    def get_all(cls):
        """取得所有提醒記錄"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM reminders").fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting all reminders: {e}")
            return []

    @classmethod
    def get_by_id(cls, reminder_id):
        """依 ID 取得提醒記錄"""
        try:
            conn = get_db_connection()
            row = conn.execute("SELECT * FROM reminders WHERE id = ?", (reminder_id,)).fetchone()
            conn.close()
            return cls(row) if row else None
        except Exception as e:
            print(f"Error getting reminder by id: {e}")
            return None

    @classmethod
    def get_by_receiver(cls, receiver_id):
        """取得發給特定使用者的所有提醒 (不包含發送者 sender_id 以保證匿名)"""
        try:
            conn = get_db_connection()
            rows = conn.execute(
                "SELECT id, group_id, receiver_id, category, message, created_at FROM reminders WHERE receiver_id = ? ORDER BY created_at DESC",
                (receiver_id,)
            ).fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting reminders by receiver: {e}")
            return []

    @classmethod
    def check_cooldown(cls, sender_id, receiver_id):
        """檢查冷卻時間：確認 sender_id 於 1 小時內是否已發送過提醒給 receiver_id"""
        try:
            conn = get_db_connection()
            row = conn.execute(
                "SELECT 1 FROM reminders WHERE sender_id = ? AND receiver_id = ? AND created_at > datetime('now', '-1 hour') LIMIT 1",
                (sender_id, receiver_id)
            ).fetchone()
            conn.close()
            return row is not None
        except Exception as e:
            print(f"Error checking cooldown: {e}")
            return True

    @classmethod
    def get_stats_by_group(cls, group_id):
        """取得特定群組匿名提醒的類別統計"""
        try:
            conn = get_db_connection()
            rows = conn.execute(
                "SELECT category, COUNT(*) as count FROM reminders WHERE group_id = ? GROUP BY category",
                (group_id,)
            ).fetchall()
            conn.close()
            return {row['category']: row['count'] for row in rows}
        except Exception as e:
            print(f"Error getting stats by group: {e}")
            return {}

    @classmethod
    def update(cls, reminder_id, data):
        """更新提醒"""
        try:
            conn = get_db_connection()
            fields = []
            values = []
            for key, val in data.items():
                fields.append(f"{key} = ?")
                values.append(val)
            values.append(reminder_id)
            query = f"UPDATE reminders SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, tuple(values))
            conn.commit()
            conn.close()
            return cls.get_by_id(reminder_id)
        except Exception as e:
            print(f"Error updating reminder: {e}")
            return None

    @classmethod
    def delete(cls, reminder_id):
        """刪除提醒"""
        try:
            conn = get_db_connection()
            conn.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting reminder: {e}")
            return False
