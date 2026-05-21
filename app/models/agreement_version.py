from app.models import get_db_connection

class AgreementVersion:
    """AgreementVersion Model — 公約版本歷史"""
    def __init__(self, row):
        self.id = row['id']
        self.agreement_id = row['agreement_id']
        self.version_number = row['version_number']
        self.content_before = row['content_before']
        self.content_after = row['content_after']
        self.modified_by = row['modified_by']
        self.created_at = row['created_at']

    def __getitem__(self, key):
        return getattr(self, key)

    @classmethod
    def create(cls, data):
        """新增一筆版本歷史"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO agreement_versions (agreement_id, version_number, content_before, content_after, modified_by) VALUES (?, ?, ?, ?, ?)",
                (data.get('agreement_id'), data.get('version_number'), data.get('content_before'), data.get('content_after'), data.get('modified_by'))
            )
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return cls.get_by_id(new_id)
        except Exception as e:
            print(f"Error creating agreement version: {e}")
            return None

    @classmethod
    def get_all(cls):
        """取得所有版本歷史"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM agreement_versions").fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting all agreement versions: {e}")
            return []

    @classmethod
    def get_by_id(cls, version_id):
        """依 ID 取得版本歷史"""
        try:
            conn = get_db_connection()
            row = conn.execute("SELECT * FROM agreement_versions WHERE id = ?", (version_id,)).fetchone()
            conn.close()
            return cls(row) if row else None
        except Exception as e:
            print(f"Error getting agreement version by id: {e}")
            return None

    @classmethod
    def get_by_agreement(cls, agreement_id):
        """取得特定公約的所有版本歷史，依版本號降冪排列"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM agreement_versions WHERE agreement_id = ? ORDER BY version_number DESC", (agreement_id,)).fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting versions by agreement: {e}")
            return []

    @classmethod
    def update(cls, version_id, data):
        """更新版本歷史"""
        try:
            conn = get_db_connection()
            fields = []
            values = []
            for key, val in data.items():
                fields.append(f"{key} = ?")
                values.append(val)
            values.append(version_id)
            query = f"UPDATE agreement_versions SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, tuple(values))
            conn.commit()
            conn.close()
            return cls.get_by_id(version_id)
        except Exception as e:
            print(f"Error updating agreement version: {e}")
            return None

    @classmethod
    def delete(cls, version_id):
        """刪除版本歷史"""
        try:
            conn = get_db_connection()
            conn.execute("DELETE FROM agreement_versions WHERE id = ?", (version_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting agreement version: {e}")
            return False
