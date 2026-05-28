"""
Group Model — 群組
儲存寢室或租屋群組的資料，並相容於 sqlite3 字典讀取與類別方法。
"""

from datetime import datetime
from app.models import db


class Group(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    invite_code = db.Column(db.String(20), unique=True, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 關聯
    creator = db.relationship('User', backref='created_groups', foreign_keys=[created_by])

    def __repr__(self):
        return f'<Group {self.name}>'

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
        """建立新群組。支援 dict 參數與 keyword 參數兩者。"""
        if args and isinstance(args[0], dict):
            data = args[0]
            group = cls(
                name=data.get('name'),
                invite_code=data.get('invite_code'),
                created_by=data.get('created_by')
            )
            db.session.add(group)
            db.session.commit()
            return group.id
        else:
            name = kwargs.get('name') or (args[0] if len(args) > 0 else None)
            invite_code = kwargs.get('invite_code') or (args[1] if len(args) > 1 else None)
            created_by = kwargs.get('created_by') or (args[2] if len(args) > 2 else None)
            group = cls(
                name=name,
                invite_code=invite_code,
                created_by=created_by
            )
            db.session.add(group)
            db.session.commit()
            return group

    @classmethod
    def get_all(cls):
        """取得所有群組"""
        return cls.query.all()

    @classmethod
    def get_by_id(cls, group_id):
        """依 ID 取得群組"""
        if group_id is None:
            return None
        return cls.query.get(group_id)

    @classmethod
    def get_by_invite_code(cls, invite_code):
        """依邀請碼取得群組"""
        return cls.query.filter_by(invite_code=invite_code).first()

    def update(self, *args, **kwargs):
        """更新群組資料。支援實例方法與靜態方法兩用。"""
        if isinstance(self, Group):
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            db.session.commit()
            return self
        else:
            group_id = self
            data = args[0] if args else kwargs
            group = Group.query.get(group_id)
            if group:
                for key, value in data.items():
                    if hasattr(group, key):
                        setattr(group, key, value)
                db.session.commit()
                return True
            return False

    def delete(self):
        """刪除群組。支援實例方法與靜態方法兩用。"""
        if isinstance(self, Group):
            db.session.delete(self)
            db.session.commit()
            return True
        else:
            group_id = self
            group = Group.query.get(group_id)
            if group:
                db.session.delete(group)
                db.session.commit()
                return True
            return False
