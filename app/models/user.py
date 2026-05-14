"""
User Model — 使用者
儲存系統所有使用者的帳號資料
"""

from datetime import datetime
from flask_login import UserMixin
from app.models import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    nickname = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='member')
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 關聯
    group = db.relationship('Group', backref='members', foreign_keys=[group_id])

    def __repr__(self):
        return f'<User {self.nickname} ({self.email})>'

    # ===== CRUD 方法 =====

    @classmethod
    def create(cls, email, password_hash, nickname, role='member', group_id=None):
        """建立新使用者"""
        user = cls(
            email=email,
            password_hash=password_hash,
            nickname=nickname,
            role=role,
            group_id=group_id
        )
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def get_all(cls):
        """取得所有使用者"""
        return cls.query.all()

    @classmethod
    def get_by_id(cls, user_id):
        """依 ID 取得使用者"""
        return cls.query.get(user_id)

    @classmethod
    def get_by_email(cls, email):
        """依 Email 取得使用者"""
        return cls.query.filter_by(email=email).first()

    def update(self, **kwargs):
        """更新使用者資料"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        """刪除使用者"""
        db.session.delete(self)
        db.session.commit()
