from app.models import get_db_connection

class MeterReading:
    """MeterReading Model — 電表度數"""
    def __init__(self, row):
        self.id = row['id']
        self.bill_id = row['bill_id']
        self.user_id = row['user_id']
        self.start_reading = row['start_reading']
        self.end_reading = row['end_reading']
        self.personal_kwh = row['personal_kwh']

    def __getitem__(self, key):
        return getattr(self, key)

    @classmethod
    def create(cls, data):
        """登錄電表度數，自動計算 personal_kwh = end - start"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            personal_kwh = float(data.get('end_reading')) - float(data.get('start_reading'))
            cursor.execute(
                "INSERT INTO meter_readings (bill_id, user_id, start_reading, end_reading, personal_kwh) VALUES (?, ?, ?, ?, ?)",
                (data.get('bill_id'), data.get('user_id'), data.get('start_reading'), data.get('end_reading'), personal_kwh)
            )
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return cls.get_by_id(new_id)
        except Exception as e:
            print(f"Error creating meter reading: {e}")
            return None

    @classmethod
    def get_all(cls):
        """取得所有度數記錄"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM meter_readings").fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting all meter readings: {e}")
            return []

    @classmethod
    def get_by_id(cls, reading_id):
        """依 ID 取得度數記錄"""
        try:
            conn = get_db_connection()
            row = conn.execute("SELECT * FROM meter_readings WHERE id = ?", (reading_id,)).fetchone()
            conn.close()
            return cls(row) if row else None
        except Exception as e:
            print(f"Error getting meter reading by id: {e}")
            return None

    @classmethod
    def get_by_bill(cls, bill_id):
        """取得特定帳單的所有電表度數記錄"""
        try:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM meter_readings WHERE bill_id = ?", (bill_id,)).fetchall()
            conn.close()
            return [cls(row) for row in rows]
        except Exception as e:
            print(f"Error getting readings by bill: {e}")
            return []

    @classmethod
    def update(cls, reading_id, data):
        """更新電表度數"""
        try:
            conn = get_db_connection()
            fields = []
            values = []
            for key, val in data.items():
                fields.append(f"{key} = ?")
                values.append(val)
            
            if 'start_reading' in data or 'end_reading' in data:
                current = cls.get_by_id(reading_id)
                start = float(data.get('start_reading', current.start_reading))
                end = float(data.get('end_reading', current.end_reading))
                fields.append("personal_kwh = ?")
                values.append(end - start)

            values.append(reading_id)
            query = f"UPDATE meter_readings SET {', '.join(fields)} WHERE id = ?"
            conn.execute(query, tuple(values))
            conn.commit()
            conn.close()
            return cls.get_by_id(reading_id)
        except Exception as e:
            print(f"Error updating meter reading: {e}")
            return None

    @classmethod
    def delete(cls, reading_id):
        """刪除度數記錄"""
        try:
            conn = get_db_connection()
            conn.execute("DELETE FROM meter_readings WHERE id = ?", (reading_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting meter reading: {e}")
            return False
