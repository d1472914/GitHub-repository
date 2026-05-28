"""
User Model — 使用者
儲存系統所有使用者的帳號資料，並相容於 sqlite3 字典讀取與類別方法。
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

    # ===== Dict-like 相容方法 =====
    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(key)

    def get(self, key, default=None):
        return getattr(self, key, default)

    # ===== CRUD 方法 =====

    @classmethod
    def create(cls, *args, **kwargs):
        """建立新使用者。支援 dict 參數與 keyword 參數兩者。"""
        if args and isinstance(args[0], dict):
            data = args[0]
            user = cls(
                email=data.get('email'),
                password_hash=data.get('password_hash'),
                nickname=data.get('nickname'),
                role=data.get('role', 'member'),
                group_id=data.get('group_id')
            )
            db.session.add(user)
            db.session.commit()
            return user.id
        else:
            email = kwargs.get('email') or (args[0] if len(args) > 0 else None)
            password_hash = kwargs.get('password_hash') or (args[1] if len(args) > 1 else None)
            nickname = kwargs.get('nickname') or (args[2] if len(args) > 2 else None)
            role = kwargs.get('role', 'member')
            group_id = kwargs.get('group_id') or (args[4] if len(args) > 4 else None)
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
        if user_id is None:
            return None
        return cls.query.get(user_id)

    @classmethod
    def get_by_email(cls, email):
        """依 Email 取得使用者"""
        return cls.query.filter_by(email=email).first()

    @classmethod
    def get_by_group_id(cls, group_id):
        """依群組 ID 取得使用者列表"""
        return cls.query.filter_by(group_id=group_id).all()

    def update(self, *args, **kwargs):
        """更新使用者資料。支援實例方法與靜態方法兩用。"""
        if isinstance(self, User):
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            db.session.commit()
            return self
        else:
            user_id = self
            data = args[0] if args else kwargs
            user = User.query.get(user_id)
            if user:
                for key, value in data.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                db.session.commit()
                return True
            return False

    def delete(self):
        """刪除使用者。支援實例方法與靜態方法兩用。"""
        if isinstance(self, User):
            db.session.delete(self)
            db.session.commit()
            return True
        else:
            user_id = self
            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
                return True
            return False
