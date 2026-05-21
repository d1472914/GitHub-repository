"""
AgreementApproval Model — 公約同意/表決記錄
記錄每位室友對公約的表決狀態、意見，並自動觸發公約狀態結算
"""

from datetime import datetime, timezone
from app.models import db


class AgreementApproval(db.Model):
    __tablename__ = 'agreement_approvals'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 加上 ondelete='CASCADE'，當公約被修訂、刪除或重置時，舊的投票紀錄會自動清空
    agreement_id = db.Column(db.Integer, db.ForeignKey('agreements.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 🔥 功能擴充：支援贊成與反對（True 為贊成，False 為反對）
    is_approved = db.Column(db.Boolean, nullable=False, default=True)
    # 🔥 功能擴充：允許留理由（特別是投反對票時，需要寫原因）
    comment = db.Column(db.String(250), nullable=True)
    
    # 修正：避免 datetime.utcnow() 棄用警告
    approved_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # 唯一約束：每人每約只能投一次票（投過只能用更新的）
    __table_args__ = (
        db.UniqueConstraint('agreement_id', 'user_id', name='uq_agreement_user'),
    )

    # 關聯
    user = db.relationship('User', backref='agreement_approvals')

    def __repr__(self):
        status = "Approve" if self.is_approved else "Reject"
        return f'<AgreementApproval agreement={self.agreement_id} user={self.user_id} status={status}>'

    # ==========================================
    # 🔥 核心功能 1：智慧投票與自動覆蓋 (Smart Vote)
    # ==========================================

    @classmethod
    def cast_vote(cls, agreement_id, user_id, is_approved=True, comment=None, commit=True):
        """
        【智慧投票核心】
        室友進行投票。如果該室友「沒投過」，會新建紀錄；
        如果「已經投過」，會自動改寫原本的決定（允許室友在截止前反悔改票）。
        """
        # 1. 檢查是否已經投過
        existing_vote = cls.query.filter_by(agreement_id=agreement_id, user_id=user_id).first()
        
        if existing_vote:
            # 投過了就更新內容
            existing_vote.is_approved = is_approved
            existing_vote.comment = comment
            existing_vote.approved_at = datetime.now(timezone.utc)
            vote = existing_vote
        else:
            # 沒投過就新增
            vote = cls(
                agreement_id=agreement_id,
                user_id=user_id,
                is_approved=is_approved,
                comment=comment
            )
            db.session.add(vote)
        
        # 2. 為了讓自動結算能拿到資料，必須先 flush 進資料庫（但先不 commit）
        db.session.flush()

        # 3. 觸發核心功能 2：去檢查這張票投完後，公約是否過關了
        cls.evaluate_agreement_status(agreement_id)

        if commit:
            db.session.commit()
        return vote

    # ==========================================
    # 🔥 核心功能 2：自動結算與狀態機流轉 (Auto Settlement)
    # ==========================================

    @classmethod
    def evaluate_agreement_status(cls, agreement_id):
        """
        【自動結算核心】
        當有人投下新的一票時，此功能會自動啟動：
        1. 撈出這條公約所屬房間（Group）的總室友數。
        2. 統計目前「贊成」與「反對」的人數。
        3. 如果全員贊成，自動把 Agreement 狀態改成 'active'（並觸發版本儲存）。
        4. 如果有人反對，自動把 Agreement 狀態改成 'rejected'。
        """
        from app.models.agreement import Agreement
        from app.models.agreement_version import AgreementVersion

        agreement = db.session.get(Agreement, agreement_id)
        if not agreement:
            return

        # 取得這個房間群組的總室友人數 (假設你的 Group Model 有 members 關聯)
        # 如果群組不存在或沒成員，預設至少為 1
        total_members = len(agreement.group.members) if (agreement.group and hasattr(agreement.group, 'members')) else 1

        # 統計當前這條公約的投票狀況
        all_votes = cls.query.filter_by(agreement_id=agreement_id).all()
        approve_count = sum(1 for v in all_votes if v.is_approved)
        reject_count = sum(1 for v in all_votes if not v.is_approved)

        # ✦ 決策邏輯 A：全員通過制 (100% 同意才生效)
        if approve_count >= total_members:
            agreement.status = 'active'
            # 公約一經表決通過，立馬觸發 AgreementVersion 幫目前的內容拍照存歷史紀錄
            AgreementVersion.save_version_snapshot(
                agreement=agreement,
                modified_by=agreement.created_by,
                change_summary="全體室友投票通過，公約正式生效！",
                commit=False
            )
        
        # ✦ 決策邏輯 B：一票否決制 (有人投反對，公約立刻被駁回)
        elif reject_count > 0:
            agreement.status = 'rejected'
        
        # ✦ 決策邏輯 C：還有人沒投，或是大家還在拉鋸
        else:
            agreement.status = 'pending'

    # ==========================================
    # 🔥 核心功能 3：取得投票進度報告 (Progress Report)
    # ==========================================

    @classmethod
    def get_progress(cls, agreement_id):
        """
        回傳結構化的投票進度，方便前端拉出進度條。
        """
        from app.models.agreement import Agreement
        agreement = db.session.get(Agreement, agreement_id)
        total_members = len(agreement.group.members) if (agreement.group and hasattr(agreement.group, 'members')) else 1

        all_votes = cls.query.filter_by(agreement_id=agreement_id).all()
        
        report = {
            "agreement_id": agreement_id,
            "total_required": total_members,
            "voted_count": len(all_votes),
            "approved": [],
            "rejected": []
        }

        for vote in all_votes:
            user_info = {"user_id": vote.user_id, "name": vote.user.name if hasattr(vote.user, 'name') else "室友", "comment": vote.comment}
            if vote.is_approved:
                report["approved"].append(user_info)
            else:
                report["rejected"].append(user_info)

        return report

    # ===== 基礎 CRUD 方法（優化為 2.0 語法） =====

    @classmethod
    def get_by_id(cls, approval_id):
        return db.session.get(cls, approval_id)

    @classmethod
    def get_by_agreement(cls, agreement_id):
        return cls.query.filter_by(agreement_id=agreement_id).all()

    @classmethod
    def has_approved(cls, agreement_id, user_id):
        """檢查某使用者是否已經投過【贊成票】"""
        vote = cls.query.filter_by(agreement_id=agreement_id, user_id=user_id).first()
        return vote is not None and vote.is_approved

    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            db.session.commit()
        return True