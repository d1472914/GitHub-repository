from app.models import get_db_connection

class AgreementApproval:
    """AgreementApproval Model — 公約同意記錄"""
    def __init__(self, row):
        self.id = row['id']
        self.agreement_id = row['agreement_id']
        self.user_id = row['user_id']
        self.approved_at = row['approved_at']

    def __getitem__(self, key):
        return getattr(self, key)

    @classmethod
    def create(cls, data):
        """建立同意記錄"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO agreement_approvals (agreement_id, user_id) VALUES (?, ?)",
                (data.get('agreement_id'), data.get('user_id'))
            )
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return cls.get_by_id(new_id)
        except Exception as e:
            print(f"Error creating agreement approval: {e}")
            return None

    @classmethod
    def get_all(cls):
        """取得所有同意記錄"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM agreement_approvals").fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting all agreement approvals: {e}")
            return []

    @classmethod
    def get_by_id(cls, approval_id):
        """依 ID 取得同意記錄"""
        try:
            conn = get_db_connection()
            row = conn.execute("SELECT * FROM agreement_approvals WHERE id = ?", (approval_id,)).fetchone()
            conn.close()
            return cls(row) if row else None
        except Exception as e:
            print(f"Error getting agreement approval by id: {e}")
            return None

    @classmethod
    def get_approvals_by_agreement(cls, agreement_id):
        """取得特定公約的所有同意記錄"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM agreement_approvals WHERE agreement_id = ?", (agreement_id,)).fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting approvals by agreement: {e}")
            return []

    @classmethod
    def has_approved(cls, agreement_id, user_id):
        """檢查特定使用者是否已同意特定公約"""
        try:
            conn = get_db_connection()
            row = conn.execute("SELECT 1 FROM agreement_approvals WHERE agreement_id = ? AND user_id = ?", (agreement_id, user_id)).fetchone()
            conn.close()
            return row is not None
        except Exception as e:
            print(f"Error checking if user has approved: {e}")
            return False

    @classmethod
    def delete_by_agreement(cls, agreement_id):
        """刪除特定公約的所有同意記錄 (公約內容修改時重設同意狀態)"""
        try:
            conn = get_db_connection()
            conn.execute("DELETE FROM agreement_approvals WHERE agreement_id = ?", (agreement_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting approvals by agreement: {e}")
            return False

    @classmethod
    def update(cls, approval_id, data):
        """更新同意記錄"""
        try:
            conn = get_db_connection()
            fields = []
            values = []
            for key, val in data.items():
                fields.append(f"{key} = ?")
                values.append(val)
            values.append(approval_id)
            query = f"UPDATE agreement_approvals SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, tuple(values))
            conn.commit()
            conn.close()
            return cls.get_by_id(approval_id)
        except Exception as e:
            print(f"Error updating agreement approval: {e}")
            return None

    @classmethod
    def delete(cls, approval_id):
        """刪除單筆同意記錄"""
        try:
            conn = get_db_connection()
            conn.execute("DELETE FROM agreement_approvals WHERE id = ?", (approval_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting agreement approval: {e}")
            return False
