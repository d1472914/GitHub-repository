"""
Group Model — 群組
儲存寢室或租屋群組的資料
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

    # ===== CRUD 方法 =====

    @classmethod
    def create(cls, name, invite_code, created_by):
        """建立新群組"""
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
        return cls.query.get(group_id)

    @classmethod
    def get_by_invite_code(cls, invite_code):
        """依邀請碼取得群組"""
        return cls.query.filter_by(invite_code=invite_code).first()

    def update(self, **kwargs):
        """更新群組資料"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        """刪除群組"""
        db.session.delete(self)
        db.session.commit()
