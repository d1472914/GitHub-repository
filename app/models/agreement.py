"""
Agreement Model — 公約
儲存室友公約的最新內容
"""

from datetime import datetime
from app.models import db


class Agreement(db.Model):
    __tablename__ = 'agreements'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    group = db.relationship('Group', backref='agreements')
    creator = db.relationship('User', backref='created_agreements')
    versions = db.relationship('AgreementVersion', backref='agreement', lazy='dynamic',
                               order_by='AgreementVersion.version_number.desc()')
    approvals = db.relationship('AgreementApproval', backref='agreement', lazy='dynamic')

    def __repr__(self):
        return f'<Agreement {self.title}>'

    # ===== CRUD 方法 =====

    @classmethod
    def create(cls, group_id, title, category, content, created_by):
        """建立新公約"""
        agreement = cls(
            group_id=group_id,
            title=title,
            category=category,
            content=content,
            created_by=created_by
        )
        db.session.add(agreement)
        db.session.commit()
        return agreement

    @classmethod
    def get_all(cls):
        """取得所有公約"""
        return cls.query.all()

    @classmethod
    def get_by_id(cls, agreement_id):
        """依 ID 取得公約"""
        return cls.query.get(agreement_id)

    @classmethod
    def get_by_group(cls, group_id):
        """取得群組的所有公約"""
        return cls.query.filter_by(group_id=group_id).order_by(cls.updated_at.desc()).all()

    def update(self, **kwargs):
        """更新公約"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self

    def delete(self):
        """刪除公約"""
        db.session.delete(self)
        db.session.commit()
