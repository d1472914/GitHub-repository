"""
AgreementVersion Model — 公約版本歷史
每次公約修改時，記錄修改前後的差異
"""

from datetime import datetime
from app.models import db


class AgreementVersion(db.Model):
    __tablename__ = 'agreement_versions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    agreement_id = db.Column(db.Integer, db.ForeignKey('agreements.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    content_before = db.Column(db.Text, nullable=True)
    content_after = db.Column(db.Text, nullable=False)
    modified_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 關聯
    modifier = db.relationship('User', backref='agreement_modifications')

    def __repr__(self):
        return f'<AgreementVersion agreement={self.agreement_id} v{self.version_number}>'

    # ===== CRUD 方法 =====

    @classmethod
    def create(cls, agreement_id, version_number, content_after, modified_by, content_before=None):
        """建立新版本記錄"""
        version = cls(
            agreement_id=agreement_id,
            version_number=version_number,
            content_before=content_before,
            content_after=content_after,
            modified_by=modified_by
        )
        db.session.add(version)
        db.session.commit()
        return version

    @classmethod
    def get_all(cls):
        """取得所有版本記錄"""
        return cls.query.all()

    @classmethod
    def get_by_id(cls, version_id):
        """依 ID 取得版本"""
        return cls.query.get(version_id)

    @classmethod
    def get_by_agreement(cls, agreement_id):
        """取得某公約的所有版本（由新到舊）"""
        return cls.query.filter_by(agreement_id=agreement_id)\
            .order_by(cls.version_number.desc()).all()

    def update(self, **kwargs):
        """更新版本記錄"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        """刪除版本記錄"""
        db.session.delete(self)
        db.session.commit()
