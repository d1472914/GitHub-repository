import difflib
from datetime import datetime, timezone
from app.models import db
from sqlalchemy import select, func

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

    # 聯合唯一索引：確保同一個公約不會有重複的版號 (防禦性設計)
    __table_args__ = (
        db.UniqueConstraint('agreement_id', 'version_number', name='uq_agreement_version'),
    )

    # 關聯
    modifier = db.relationship('User', backref='agreement_modifications')

    def __repr__(self):
        return f'<AgreementVersion agreement={self.agreement_id} v{self.version_number}>'

    # ========================================================
    # 🔥 核心功能 1：自動化追蹤生成 (優化：防止併發衝突)
    # ========================================================

    @classmethod
    def save_version_snapshot(cls, agreement, modified_by, change_summary="修訂公約", commit=False):
        """
        【全自動追蹤核心】
        利用悲觀鎖或聚合函數確保 version_number 的連續性與唯一性。
        """
        # 使用 func.max 確保在同一個事務中計算最新版號，減少 Race Condition
        max_version = db.session.query(func.max(cls.version_number))\
            .filter(cls.agreement_id == agreement.id).scalar()

        if max_version is None:
            version_number = 1
            content_before = None
        else:
            version_number = max_version + 1
            # 抓取上一版的 content_after
            last_version = cls.query.filter_by(agreement_id=agreement.id, version_number=max_version).first()
            content_before = last_version.content_after if last_version else None

        # 建立快照紀錄
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
    # 🔥 核心功能 2：高階文字差異比對 (優化：加入行內字元級比對)
    # ========================================================

    def get_diff_report(self):
        """
        比對 content_before 與 content_after，
        除了回傳行變更 (replace/delete/insert)，若是 replace，額外提供行內的字元級差異。
        """
        if not self.content_before:
            return {"type": "initial", "message": "初始版本，無前文對比", "changes": []}
            
        before_lines = self.content_before.splitlines()
        after_lines = self.content_after.splitlines()
        
        matcher = difflib.SequenceMatcher(None, before_lines, after_lines)
        changes = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                continue
                
            old_lines = before_lines[i1:i2]
            new_lines = after_lines[j1:j2]
            inline_diff = None

            # 🌟 進階優化：如果該行是被「修改(replace)」，進行行內細部字元比對
            if tag == 'replace' and len(old_lines) == 1 and len(new_lines) == 1:
                inline_matcher = difflib.SequenceMatcher(None, old_lines[0], new_lines[0])
                inline_diff = {
                    "old_words": [],
                    "new_words": []
                }
                for sub_tag, si1, si2, sj1, sj2 in inline_matcher.get_opcodes():
                    inline_diff["old_words"].append({"type": sub_tag, "text": old_lines[0][si1:si2]})
                    inline_diff["new_words"].append({"type": sub_tag, "text": new_lines[0][sj1:sj2]})
            
            changes.append({
                "type": tag,
                "old_lines": old_lines,
                "new_lines": new_lines,
                "old_range": [i1, i2],
                "new_range": [j1, j2],
                "inline_diff": inline_diff  # 提供給前端做更精細的 markup (如 <s> 或 <mark>)
            })
            
        return {
            "type": "modification",
            "version": self.version_number,
            "change_summary": self.change_summary,
            "changes": changes
        }

    # ========================================================
    # 🔥 核心功能 3：一鍵回滾/還原歷史 (優化：回滾視為一次新修訂)
    # ========================================================

    def rollback_agreement(self, operator_id, commit=True):
        """
        將公約內容還原至此版本的狀態。
        安全做法：修改 Agreement 內容後，必須呼叫 `save_version_snapshot` 生成新版本紀錄（如 v4 內容同 v2）。
        """
        from app.models.agreement import Agreement
        agreement = db.session.get(Agreement, self.agreement_id)
        if not agreement:
            raise ValueError("找不到關聯的公約本體，無法還原。")

        # 1. 更新公約主體狀態
        agreement.title = self.title
        agreement.content = self.content_after  # 歷史版本的修改後內容，就是我們要還原的目標
        agreement.status = 'pending'  # 退回待審核
        
        # 2. 清除舊的投票紀錄（安全清除防呆）
        if hasattr(agreement, 'approvals') and agreement.approvals:
            # 假設 approvals 是 relationship 且配置了 lazy='dynamic' 或 cascade
            agreement.approvals.clear() 
        
        # 🌟 重大完善：回滾必須產生一筆新的版本歷史，否則歷史鏈會斷掉！
        summary = f"回滾公約至版本 v{self.version_number}"
        db.session.flush() # 先讓 agreement 的變更對資料庫可見（但未 commit）
        
        # 產生新版快照
        cls.save_version_snapshot(
            agreement=agreement, 
            modified_by=operator_id, 
            change_summary=summary, 
            commit=False
        )
        
        if commit:
            db.session.commit()
        return agreement

    # ===== 基礎 CRUD 方法 =====

    @classmethod
    def get_by_id(cls, version_id):
        return db.session.get(cls, version_id)

    @classmethod
    def get_by_agreement(cls, agreement_id):
        """依據公約 ID 撈出所有的版本紀錄（新 -> 舊）"""
        return cls.query.filter_by(agreement_id=agreement_id)\
                         .order_by(cls.version_number.desc()).all()

    def delete(self, commit=True):
        """審計合規：歷史紀錄一般禁止單獨刪除"""
        raise NotImplementedError("為了維護公約變更的審計完整性，禁止單獨刪除歷史版本紀錄。")