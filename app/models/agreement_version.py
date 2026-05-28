"""
AgreementVersion Model — 公約版本歷史
每次公約修改時，自動記錄修改前後的差異與版本控制
"""

import difflib
from datetime import datetime, timezone
from app.models import db


class AgreementVersion(db.Model):
    __tablename__ = 'agreement_versions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, nullable=False)  # 快照備份：群組 ID
    agreement_id = db.Column(db.Integer, db.ForeignKey('agreements.id', ondelete='CASCADE'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)  # 快照備份：當時標題
    content_before = db.Column(db.Text, nullable=True)  # 修改前內容（V1 時為 Null）
    content_after = db.Column(db.Text, nullable=False)  # 修改後內容
    change_summary = db.Column(db.String(250), nullable=True)  # 修改原因
    modified_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # 關聯
    modifier = db.relationship('User', backref='agreement_modifications')

    def __repr__(self):
        return f'<AgreementVersion agreement={self.agreement_id} v{self.version_number}>'

    # ========================================================
    # 🔥 核心功能 1：自動化追蹤生成 (Auto Version Creator)
    # ========================================================

    @classmethod
    def save_version_snapshot(cls, agreement, modified_by, change_summary="修訂公約", commit=False):
        """
        【全自動追蹤核心】
        直接丟入 Agreement 物件，這個方法會自己判定它是 V1 還是修訂版、
        自動去抓上一版的內容當作 content_before、自動計算下一個版號並儲存。
        """
        # 1. 查詢該公約目前的最新版本紀錄
        latest_version = cls.query.filter_by(agreement_id=agreement.id)\
                                  .order_by(cls.version_number.desc())\
                                  .first()
        
        if not latest_version:
            # 代表這是剛建立的公約草案 (V1)
            version_number = 1
            content_before = None
        else:
            # 代表是後續的修改 (V2, V3...)
            version_number = latest_version.version_number + 1
            # 把上一次的「修改後內容」，當作這一次的「修改前內容」
            content_before = latest_version.content_after

        # 2. 建立快照紀錄
        new_version = cls(
            agreement_id=agreement.id,
            group_id=agreement.group_id,
            version_number=version_number,
            title=agreement.title,
            content_before=content_before,
            content_after=agreement.content,  # 目前最新的內容
            change_summary=change_summary,
            modified_by=modified_by
        )
        
        db.session.add(new_version)
        if commit:
            db.session.commit()
            
        return new_version

    # ========================================================
    # 🔥 核心功能 2：高階文字差異比對 (Advanced Text Diff)
    # ========================================================

    def get_diff_report(self):
        """
        將 content_before 與 content_after 做行對行比對，
        回傳前端可以直接拿來渲染紅綠色（新增/刪除）的結構化 JSON 資料。
        """
        if not self.content_before:
            return {"type": "initial", "message": "初始版本，無前文對比", "changes": []}
            
        before_lines = self.content_before.splitlines()
        after_lines = self.content_after.splitlines()
        
        # 使用 Python 內建 of SequenceMatcher
        matcher = difflib.SequenceMatcher(None, before_lines, after_lines)
        changes = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            # tag 有四種：'equal' (沒變), 'replace' (修改), 'delete' (刪除), 'insert' (新增)
            if tag == 'equal':
                continue
                
            changes.append({
                "type": tag,
                "old_lines": before_lines[i1:i2],
                "new_lines": after_lines[j1:j2],
                "old_range": [i1, i2],
                "new_range": [j1, j2]
            })
            
        return {
            "type": "modification",
            "version": self.version_number,
            "change_summary": self.change_summary,
            "changes": changes
        }

    # ========================================================
    # 🔥 核心功能 3：一鍵回滾/還原歷史 (Rollback Mechanism)
    # ========================================================

    def rollback_agreement(self, operator_id, commit=True):
        """
        直接用這個歷史版本覆蓋公約目前最新的內容。
        注意：這會觸發一輪新的「提案修改」，公約狀態會退回 pending 讓室友重新投票。
        """
        from app.models.agreement import Agreement
        agreement = db.session.get(Agreement, self.agreement_id)
        if not agreement:
            raise ValueError("找不到關聯的公約本體，無法還原。")

        # 把公約內容改回這一個版本的歷史文字
        agreement.title = self.title
        agreement.content = self.content_after
        agreement.status = 'pending'  # 退回待審核
        
        # 清除舊的投票紀錄（內容變了必須重新投票）
        agreement.approvals.delete()
        
        if commit:
            db.session.commit()
        return agreement

    # ===== 基礎 CRUD 方法 (優化版) =====

    @classmethod
    def get_by_id(cls, version_id):
        return db.session.get(cls, version_id)

    @classmethod
    def get_by_agreement(cls, agreement_id):
        """依據公約 ID 撈出所有的版本紀錄（新 -> 舊）"""
        return cls.query.filter_by(agreement_id=agreement_id)\
                        .order_by(cls.version_number.desc()).all()

    def delete(self, commit=True):
        """歷史紀錄一般不給刪，除非整組清掉"""
        db.session.delete(self)
        if commit:
            db.session.commit()
        return True