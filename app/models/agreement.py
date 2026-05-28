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
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, active, rejected
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 全面改用帶時區的 UTC 時間，預防跨時區伺服器解析錯誤
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # 關聯
    group = db.relationship('Group', backref=db.backref('agreements', lazy='dynamic', cascade='all, delete-orphan'))
    creator = db.relationship('User', backref='created_agreements')
    
    # 🌟 cascade 配置優化：刪除公約時，一併乾淨抹除關聯的版本與投票，拒絕孤兒數據
    versions = db.relationship('AgreementVersion', backref='agreement', lazy='dynamic',
                               cascade="all, delete-orphan",
                               order_by='AgreementVersion.version_number.desc()')
    approvals = db.relationship('AgreementApproval', backref='agreement', lazy='dynamic',
                                cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Agreement {self.title} status={self.status}>'

    # ===== Dict-like 相容方法 =====
    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(key)

    def get(self, key, default=None):
        return getattr(self, key, default)

    # ========================================================
    # 核心 CRUD 與業務邏輯方法
    # ========================================================

    @classmethod
    def create_agreement(cls, group_id, title, category, content, created_by, status='pending', commit=True):
        """建立新公約，並自動產生 V1 歷史版本快照"""
        agreement = cls(
            group_id=group_id,
            title=title,
            category=category,
            content=content,
            status=status,
            created_by=created_by
        )
        db.session.add(agreement)
        db.session.flush()  # 先取得公約 id，以便關聯版本歷史

        # 呼叫 AgreementVersion 的高階全自動建立快照方法
        from app.models.agreement_version import AgreementVersion
        AgreementVersion.save_version_snapshot(
            agreement=agreement,
            modified_by=created_by,
            change_summary="建立初始公約 (V1)",
            commit=False
        )

        if commit:
            db.session.commit()
        return agreement

    @classmethod
    def get_by_id(cls, agreement_id):
        return db.session.get(cls, agreement_id)

    @classmethod
    def get_by_group(cls, group_id):
        return cls.query.filter_by(group_id=group_id).order_by(cls.updated_at.desc()).all()

    def update_agreement(self, data, modified_by, commit=True):
        """
        更新公約內容。
        🌟 修正：只要 title 或 content 被修改，皆視為重大更新：
        1. 自動將狀態退回 'pending' 重啟投票。
        2. 安全清空舊的投票紀錄。
        3. 自動呼叫 `AgreementVersion` 生成下一版差異紀錄（含標題快照）。
        """
        old_title = self.title
        old_content = self.content
        
        new_title = data.get('title', old_title)
        new_content = data.get('content', old_content)
        
        # 🌟 核心修正 1：擴大變更判定範圍，將 title 納入合規審查
        core_changed = (new_content != old_content) or (new_title != old_title)

        # 1. 欄位賦值
        if 'title' in data:
            self.title = new_title
        if 'category' in data:
            self.category = data['category']
        if 'content' in data:
            self.content = new_content
        if 'status' in data:
            self.status = data['status']
            
        # 2. 核心欄位有變動時的商業邏輯處理
        if core_changed:
            self.status = 'pending'
            
            # 🌟 核心修正 2：改用 ORM 級別的清空，避免直接 delete() 繞過緩存控制
            from app.models.agreement_approval import AgreementApproval
            AgreementApproval.query.filter_by(agreement_id=self.id).delete(synchronize_session='fetch')
            
            db.session.flush()  # 讓欄位變更在 session 內生效，以便快照抓取最新狀態

            # 生成下一版歷史快照
            from app.models.agreement_version import AgreementVersion
            AgreementVersion.save_version_snapshot(
                agreement=self,
                modified_by=modified_by,
                change_summary=data.get('change_summary', '修訂公約內容'),
                commit=False
            )

        if commit:
            db.session.commit()
        return True

    def add_approval(self, user_id, commit=True):
        """對此公約進行室友投票，並自動判定是否全員通過觸發啟用"""
        # 🌟 核心修正 3：狀態防禦，只有審核中的公約才能投票，防止對已生效/已拒絕的公約重複投票
        if self.status != 'pending':
            return False

        from app.models.agreement_approval import AgreementApproval
        
        # 檢查是否重複投票 (防禦性設計)
        exists = AgreementApproval.query.filter_by(agreement_id=self.id, user_id=user_id).first()
        if not exists:
            AgreementApproval.create_approval(agreement_id=self.id, user_id=user_id, commit=False)
            db.session.flush()

        # 檢查群組全員人數
        total_members = len(self.group.members) if (self.group and self.group.members) else 1
        approved_count = AgreementApproval.query.filter_by(agreement_id=self.id).count()

        # 若同意人數達到或超過群組總人數，公約即刻生效！
        if approved_count >= total_members:
            self.status = 'active'
            
        if commit:
            db.session.commit()
        return True


# ========================================================
# ⚙️ Module-level wrappers (完全對齊重構後的方法，提供測試與相容性)
# ========================================================

def create(data):
    agreement = Agreement.create_agreement(
        group_id=data.get('group_id'),
        title=data.get('title'),
        category=data.get('category'),
        content=data.get('content'),
        status=data.get('status', 'pending'),
        created_by=data.get('created_by'),
        commit=True
    )
    return agreement.id

def get_by_id(agreement_id):
    return Agreement.get_by_id(agreement_id)

def get_by_group(group_id):
    return Agreement.get_by_group(group_id)

def update(agreement_id, data):
    agreement = Agreement.get_by_id(agreement_id)
    if not agreement:
        return False
    
    modified_by = data.get('modified_by', agreement.created_by)
    return agreement.update_agreement(data, modified_by=modified_by, commit=True)

def get_versions(agreement_id):
    from app.models.agreement_version import AgreementVersion
    return AgreementVersion.get_by_agreement(agreement_id)

def approve(agreement_id, user_id):
    agreement = Agreement.get_by_id(agreement_id)
    if not agreement:
        return False
    return agreement.add_approval(user_id, commit=True)

def get_approvals(agreement_id):
    """🌟 核心修正 4：調用已優化優良的 AgreementApproval 查詢，內聯 Joinedload 阻斷 N+1 效能問題"""
    from app.models.agreement_approval import AgreementApproval
    approvals = AgreementApproval.get_by_agreement(agreement_id)
    return [
        {
            'user_id': ap.user_id,
            'nickname': ap.user.nickname if (hasattr(ap, 'user') and ap.user) else '室友'
        }
        for ap in approvals
    ]

def delete(agreement_id):
    agreement = Agreement.get_by_id(agreement_id)
    if agreement:
        db.session.delete(agreement)
        db.session.commit()
        return True
    return False
