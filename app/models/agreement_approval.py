"""
AgreementApproval Model — 公約同意/表決記錄
記錄每位室友對公約的表決狀態、意見，並自動觸發公約狀態結算
"""

from datetime import datetime, timezone
from app.models import db

class AgreementApproval(db.Model):
    __tablename__ = 'agreement_approvals'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # 🌟 優化：加入 ondelete='CASCADE'。當公約或使用者被刪除時，投票紀錄自動由資料庫抹除
    agreement_id = db.Column(db.Integer, db.ForeignKey('agreements.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # 🌟 優化：全面改用帶時區的 UTC 時間
    approved_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    # 唯一約束：每人每約只能投一次票（投過只能用更新的）
    __table_args__ = (
        db.UniqueConstraint('agreement_id', 'user_id', name='uq_agreement_user'),
    )

    # 關聯
    user = db.relationship('User', backref='agreement_approvals')

    def __repr__(self):
        status = "Approve" if self.is_approved else "Reject"
        return f'<AgreementApproval agreement={self.agreement_id} user={self.user_id} status={status}>'

    # ========================================================
    # 核心 業務邏輯與 CRUD 方法
    # ========================================================

    @classmethod
    def create_approval(cls, agreement_id, user_id, commit=True):
        """
        建立同意記錄。
        🌟 修正：將方法名改為 create_approval，完美對齊 Agreement 的內部呼叫。
        """
        # 安全防禦：如果已經投過票，直接回傳既有的，不重複建立
        existing = cls.query.filter_by(agreement_id=agreement_id, user_id=user_id).first()
        if existing:
            return existing

        approval = cls(
            agreement_id=agreement_id,
            user_id=user_id
        )
        db.session.add(approval)
        
        if commit:
            db.session.commit()
        return approval

    @classmethod
    def retract_approval(cls, agreement_id, user_id, commit=True):
        """
        🌟 新增功能：撤銷/收回同意票。
        只有當公約狀態還是 'pending'（審核中）時才能收回票。
        """
        from app.models.agreement import Agreement
        agreement = db.session.get(Agreement, agreement_id)
        
        if not agreement:
            raise ValueError("找不到該公約。")
        if agreement.status != 'pending':
            raise ValueError("公約已生效或已被拒絕，無法收回同意票。")

        approval = cls.query.filter_by(agreement_id=agreement_id, user_id=user_id).first()
        if approval:
            db.session.delete(approval)
            if commit:
                db.session.commit()
            return True
        return False

    @classmethod
    def get_all(cls):
        """取得所有同意記錄"""
        return cls.query.all()

    @classmethod
    def get_by_id(cls, approval_id):
        """🌟 優化：改用 SQLAlchemy 2.0 推薦的 db.session.get"""
        return db.session.get(cls, approval_id)

    @classmethod
    def get_by_agreement(cls, agreement_id):
        """取得某公約的所有同意記錄，並預先載入 user 資料（避免 N+1 查詢問題）"""
        return cls.query.filter_by(agreement_id=agreement_id).options(db.joinedload(cls.user)).all()

    @classmethod
    def has_approved(cls, agreement_id, user_id):
        """檢查某使用者是否已經投過【贊成票】"""
        vote = cls.query.filter_by(agreement_id=agreement_id, user_id=user_id).first()
        return vote is not None and vote.is_approved

    def update(self, **kwargs):
        """審計合規：投票紀錄原則上不允許直接修改 agreement_id 或 user_id"""
        for key, value in kwargs.items():
            if key in ['agreement_id', 'user_id']:
                raise AttributeError(f"不允許篡改投票紀錄的關鍵欄位: {key}")
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self, commit=True):
        """刪除同意記錄"""
        db.session.delete(self)
        if commit:
            db.session.commit()
