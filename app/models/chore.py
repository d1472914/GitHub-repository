"""
Chore Model — 家事任務
儲存隱形管家的排班任務
"""

from datetime import datetime
from app.models import db


class Chore(db.Model):
    __tablename__ = 'chores'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    recurrence = db.Column(db.String(20), nullable=False, default='once')
    due_date = db.Column(db.Date, nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 關聯
    group = db.relationship('Group', backref='chores')
    assignee = db.relationship('User', backref='assigned_chores', foreign_keys=[assigned_to])
    creator = db.relationship('User', backref='created_chores', foreign_keys=[created_by])

    def __repr__(self):
        return f'<Chore {self.title} ({self.status})>'

    # ===== CRUD 方法 =====

    @classmethod
    def create(cls, group_id, title, due_date, assigned_to, created_by,
               description=None, recurrence='once'):
        """建立新任務"""
        chore = cls(
            group_id=group_id,
            title=title,
            description=description,
            recurrence=recurrence,
            due_date=due_date,
            assigned_to=assigned_to,
            created_by=created_by
        )
        db.session.add(chore)
        db.session.commit()
        return chore

    @classmethod
    def get_all(cls):
        """取得所有任務"""
        return cls.query.all()

    @classmethod
    def get_by_id(cls, chore_id):
        """依 ID 取得任務"""
        return cls.query.get(chore_id)

    @classmethod
    def get_by_group(cls, group_id):
        """取得群組的所有任務（依到期日排序）"""
        return cls.query.filter_by(group_id=group_id)\
            .order_by(cls.due_date.asc()).all()

    @classmethod
    def get_pending_by_user(cls, user_id):
        """取得某使用者所有待完成的任務"""
        return cls.query.filter_by(assigned_to=user_id, status='pending')\
            .order_by(cls.due_date.asc()).all()

    def mark_completed(self):
        """標記任務已完成"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()
        db.session.commit()
        return self

    def update(self, **kwargs):
        """更新任務"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        """刪除任務"""
        db.session.delete(self)
        db.session.commit()
