"""
Agreement Model — 公約（完整功能版）
儲存室友公約的最新內容，並包含版本修訂與審核流轉功能
"""

from datetime import datetime, timezone
from app.models import db


class Agreement(db.Model):
    __tablename__ = 'agreements'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, active, rejected, archived
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # 關聯
    group = db.relationship('Group', backref=db.backref('agreements', lazy='dynamic', cascade='all, delete-orphan'))
    creator = db.relationship('User', backref='created_agreements')
    
    # 這裡修正了原先排序的字串寫法，確保由新到舊排序
    versions = db.relationship('AgreementVersion', backref='agreement', lazy='dynamic',
                               cascade='all, delete-orphan',
                               order_by='desc(AgreementVersion.version_number)')
    approvals = db.relationship('AgreementApproval', backref='agreement', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Agreement {self.title} ({self.status})>'

    # ==========================================
    # 核心功能 1：版本控制與修訂 (Version Control)
    # ==========================================

    def create_version(self, updater_id, change_summary="修訂公約", commit=True):
        """
        將目前公約的快照存入 AgreementVersion 模型中。
        通常在：1. 剛建立公約時 (V1) 2. 公約被修改通過後 呼叫。
        """
        # 引入你的 AgreementVersion Model (避免循環導入，可在方法內 import)
        from app.models.agreement_version import AgreementVersion

        return AgreementVersion.save_version_snapshot(
            agreement=self,
            modified_by=updater_id,
            change_summary=change_summary,
            commit=commit
        )

    def propose_revision(self, title, content, updater_id, change_summary, commit=True):
        """
        室友提議修改公約內容。
        修改後狀態會退回 'pending'，需要重新發起投票審核。
        """
        self.title = title
        self.content = content
        self.status = 'pending'  # 修改後需要重新審核
        
        # 這裡不直接建立正式版本，等大家投票過變 'active' 再建立 version 快照
        # 或者你要「修改即留底」也可以在此直接調用 self.create_version
        
        # 先清空上一輪的投票紀錄（因為內容變了，舊的同意算不算數？）
        self.approvals.delete()
        
        if commit:
            db.session.commit()
        return self

    # ==========================================
    # 核心功能 2：審核與室友投票 (Approval & Voting)
    # ==========================================

    def cast_vote(self, user_id, is_approved, comment=None, commit=True):
        """
        室友針對這項公約進行 贊成/反對 投票。
        """
        from app.models.agreement_approval import AgreementApproval

        # 檢查該室友是否投過票了，投過就更新，沒投過就新建
        vote = self.approvals.filter_by(user_id=user_id).first()
        if vote:
            vote.is_approved = is_approved
            vote.comment = comment
            vote.updated_at = datetime.now(timezone.utc)
        else:
            vote = AgreementApproval(
                agreement_id=self.id,
                user_id=user_id,
                is_approved=is_approved,
                comment=comment
            )
            db.session.add(vote)

        if commit:
            db.session.commit()
            
        # 順便觸發自動檢查：是不是大家都同意了？
        self.check_voting_result(commit=commit)
        return vote

    def check_voting_result(self, commit=True):
        """
        檢查投票結果。
        實務邏輯：如果群組內「所有室友」都同意，公約自動轉為 'active'，並產生版本紀錄。
        """
        # 取得這個群組的總人數（假設你的 Group 模型的關係是 group.members）
        total_roommates = len(self.group.members) if self.group else 1
        
        # 計算目前投同意票的人數
        approve_count = self.approvals.filter_by(is_approved=True).count()
        reject_count = self.approvals.filter_by(is_approved=False).count()

        # 方案 A：全數通過制 (100% 同意)
        if approve_count >= total_roommates:
            self.status = 'active'
            # 生效時自動封存目前的內容為歷史版本
            self.create_version(updater_id=self.created_by, change_summary="投票全數通過，正式生效", commit=False)
        
        # 方案 B：有人反對直接拒絕 (可依你的需求調整，例如過半數就通過之類的)
        elif reject_count > 0:
            self.status = 'rejected'

        if commit:
            db.session.commit()

    # ===== 基礎 CRUD 方法 =====

    @classmethod
    def create(cls, group_id, title, category, content, created_by, commit=True):
        """建立新公約，並自動生成 V1 初始版本"""
        agreement = cls(
            group_id=group_id,
            title=title,
            category=category,
            content=content,
            created_by=created_by,
            status='pending'  # 預設等大家投票
        )
        db.session.add(agreement)
        db.session.flush()  # 拿到 agreement.id 但還不提交

        # 自動幫新公約建立 V1 快照
        agreement.create_version(updater_id=created_by, change_summary="建立初始公約草案", commit=False)

        if commit:
            db.session.commit()
        return agreement

    @classmethod
    def get_by_id(cls, agreement_id):
        return db.session.get(cls, agreement_id)

    @classmethod
    def get_by_group(cls, group_id, status=None):
        query = cls.query.filter_by(group_id=group_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(cls.updated_at.desc()).all()

    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            db.session.commit()
        return True
