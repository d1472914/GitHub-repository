"""
Reminder Model — 匿名提醒
儲存友善黑臉的匿名提醒記錄
注意：sender_id 僅供冷卻機制與統計使用，不對接收者顯示
"""

from datetime import datetime, timedelta
from app.models import db


class Reminder(db.Model):
    __tablename__ = 'reminders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(30), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 關聯
    group = db.relationship('Group', backref='reminders')
    sender = db.relationship('User', backref='sent_reminders', foreign_keys=[sender_id])
    receiver = db.relationship('User', backref='received_reminders', foreign_keys=[receiver_id])

    def __repr__(self):
        return f'<Reminder {self.category} to user={self.receiver_id}>'

    # ===== CRUD 方法 =====

    @classmethod
    def create(cls, group_id, sender_id, receiver_id, category, message):
        """建立匿名提醒"""
        reminder = cls(
            group_id=group_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            category=category,
            message=message
        )
        db.session.add(reminder)
        db.session.commit()
        return reminder

    @classmethod
    def get_all(cls):
        """取得所有提醒"""
        return cls.query.all()

    @classmethod
    def get_by_id(cls, reminder_id):
        """依 ID 取得提醒"""
        return cls.query.get(reminder_id)

    @classmethod
    def get_received_by_user(cls, user_id):
        """取得某使用者收到的所有提醒（不含 sender 資訊，由新到舊）"""
        return cls.query.filter_by(receiver_id=user_id)\
            .order_by(cls.created_at.desc()).all()

    @classmethod
    def check_cooldown(cls, sender_id, receiver_id, cooldown_hours=1):
        """檢查冷卻機制：同一發送者對同一對象在指定時間內是否已發送過"""
        cooldown_time = datetime.utcnow() - timedelta(hours=cooldown_hours)
        recent = cls.query.filter(
            cls.sender_id == sender_id,
            cls.receiver_id == receiver_id,
            cls.created_at >= cooldown_time
        ).first()
        return recent is None  # True 表示可以發送

    @classmethod
    def get_stats_by_group(cls, group_id):
        """取得群組的提醒統計（類別與次數，不揭露個人）"""
        from sqlalchemy import func
        return db.session.query(
            cls.category, func.count(cls.id)
        ).filter_by(group_id=group_id).group_by(cls.category).all()

    def update(self, **kwargs):
        """更新提醒"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        """刪除提醒"""
        db.session.delete(self)
        db.session.commit()
