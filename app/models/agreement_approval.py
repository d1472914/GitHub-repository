"""
AgreementApproval Model — 公約同意記錄
記錄每位室友對公約的確認同意
"""

from datetime import datetime
from app.models import db


class AgreementApproval(db.Model):
    __tablename__ = 'agreement_approvals'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    agreement_id = db.Column(db.Integer, db.ForeignKey('agreements.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approved_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 唯一約束：每人每約只能同意一次
    __table_args__ = (
        db.UniqueConstraint('agreement_id', 'user_id', name='uq_agreement_user'),
    )

    # 關聯
    user = db.relationship('User', backref='agreement_approvals')

    def __repr__(self):
        return f'<AgreementApproval agreement={self.agreement_id} user={self.user_id}>'

    # ===== CRUD 方法 =====

    @classmethod
    def create(cls, agreement_id, user_id):
        """建立同意記錄"""
        approval = cls(
            agreement_id=agreement_id,
            user_id=user_id
        )
        db.session.add(approval)
        db.session.commit()
        return approval

    @classmethod
    def get_all(cls):
        """取得所有同意記錄"""
        return cls.query.all()

    @classmethod
    def get_by_id(cls, approval_id):
        """依 ID 取得同意記錄"""
        return cls.query.get(approval_id)

    @classmethod
    def get_by_agreement(cls, agreement_id):
        """取得某公約的所有同意記錄"""
        return cls.query.filter_by(agreement_id=agreement_id).all()

    @classmethod
    def has_approved(cls, agreement_id, user_id):
        """檢查某使用者是否已對某公約投過同意"""
        return cls.query.filter_by(
            agreement_id=agreement_id, user_id=user_id
        ).first() is not None

    def update(self, **kwargs):
        """更新同意記錄"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        """刪除同意記錄"""
        db.session.delete(self)
        db.session.commit()
