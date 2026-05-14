"""
Notification Model — 站內通知
儲存系統發送給使用者的通知訊息
"""

from datetime import datetime
from app.models import db


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    type = db.Column(db.String(30), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=True)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 關聯
    user = db.relationship('User', backref='notifications')
    group = db.relationship('Group', backref='notifications')

    def __repr__(self):
        return f'<Notification {self.title} ({self.type})>'

    # ===== CRUD 方法 =====

    @classmethod
    def create(cls, user_id, group_id, type, title, message=None):
        """建立新通知"""
        notification = cls(
            user_id=user_id,
            group_id=group_id,
            type=type,
            title=title,
            message=message
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    @classmethod
    def get_all(cls):
        """取得所有通知"""
        return cls.query.all()

    @classmethod
    def get_by_id(cls, notification_id):
        """依 ID 取得通知"""
        return cls.query.get(notification_id)

    @classmethod
    def get_by_user(cls, user_id):
        """取得某使用者的所有通知（由新到舊）"""
        return cls.query.filter_by(user_id=user_id)\
            .order_by(cls.created_at.desc()).all()

    @classmethod
    def get_unread_by_user(cls, user_id):
        """取得某使用者所有未讀通知"""
        return cls.query.filter_by(user_id=user_id, is_read=False)\
            .order_by(cls.created_at.desc()).all()

    @classmethod
    def get_unread_count(cls, user_id):
        """取得某使用者未讀通知數量"""
        return cls.query.filter_by(user_id=user_id, is_read=False).count()

    def mark_as_read(self):
        """標記為已讀"""
        self.is_read = True
        db.session.commit()

    @classmethod
    def mark_all_as_read(cls, user_id):
        """將某使用者所有通知標記為已讀"""
        cls.query.filter_by(user_id=user_id, is_read=False)\
            .update({'is_read': True})
        db.session.commit()

    def update(self, **kwargs):
        """更新通知"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        """刪除通知"""
        db.session.delete(self)
        db.session.commit()
