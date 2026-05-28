<<<<<<< HEAD
=======
"""
AgreementVersion Model — 公約版本歷史
每次公約修改時，自動記錄修改前後的差異與版本控制
"""

>>>>>>> 6c85f97630763fd1f55b75d67d815dac69d5a81d
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
<<<<<<< HEAD

    # 聯合唯一索引：確保同一個公約不會有重複的版號 (防禦性設計)
    __table_args__ = (
        db.UniqueConstraint('agreement_id', 'version_number', name='uq_agreement_version'),
    )
=======
>>>>>>> 6c85f97630763fd1f55b75d67d815dac69d5a81d

    # 關聯
    modifier = db.relationship('User', backref='agreement_modifications')

    def __repr__(self):
        return f'<AgreementVersion agreement={self.agreement_id} v{self.version_number}>'

    # ========================================================
<<<<<<< HEAD
    # 🔥 核心功能 1：自動化追蹤生成 (優化：防止併發衝突)
=======
    # 🔥 核心功能 1：自動化追蹤生成 (Auto Version Creator)
>>>>>>> 6c85f97630763fd1f55b75d67d815dac69d5a81d
    # ========================================================

    @classmethod
    def save_version_snapshot(cls, agreement, modified_by, change_summary="修訂公約", commit=False):
        """
        【全自動追蹤核心】
<<<<<<< HEAD
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
=======
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
>>>>>>> 6c85f97630763fd1f55b75d67d815dac69d5a81d
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
<<<<<<< HEAD
    # 🔥 核心功能 2：高階文字差異比對 (優化：加入行內字元級比對)
=======
    # 🔥 核心功能 2：高階文字差異比對 (Advanced Text Diff)
>>>>>>> 6c85f97630763fd1f55b75d67d815dac69d5a81d
    # ========================================================

    def get_diff_report(self):
        """
<<<<<<< HEAD
        比對 content_before 與 content_after，
        除了回傳行變更 (replace/delete/insert)，若是 replace，額外提供行內的字元級差異。
=======
        將 content_before 與 content_after 做行對行比對，
        回傳前端可以直接拿來渲染紅綠色（新增/刪除）的結構化 JSON 資料。
>>>>>>> 6c85f97630763fd1f55b75d67d815dac69d5a81d
        """
        if not self.content_before:
            return {"type": "initial", "message": "初始版本，無前文對比", "changes": []}
            
        before_lines = self.content_before.splitlines()
        after_lines = self.content_after.splitlines()
        
<<<<<<< HEAD
=======
        # 使用 Python 內建 of SequenceMatcher
>>>>>>> 6c85f97630763fd1f55b75d67d815dac69d5a81d
        matcher = difflib.SequenceMatcher(None, before_lines, after_lines)
        changes = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
<<<<<<< HEAD
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
=======
            # tag 有四種：'equal' (沒變), 'replace' (修改), 'delete' (刪除), 'insert' (新增)
            if tag == 'equal':
                continue
                
            changes.append({
                "type": tag,
                "old_lines": before_lines[i1:i2],
                "new_lines": after_lines[j1:j2],
                "old_range": [i1, i2],
                "new_range": [j1, j2]
>>>>>>> 6c85f97630763fd1f55b75d67d815dac69d5a81d
            })
            
        return {
            "type": "modification",
            "version": self.version_number,
            "change_summary": self.change_summary,
            "changes": changes
        }

    # ========================================================
<<<<<<< HEAD
    # 🔥 核心功能 3：一鍵回滾/還原歷史 (優化：回滾視為一次新修訂)
=======
    # 🔥 核心功能 3：一鍵回滾/還原歷史 (Rollback Mechanism)
>>>>>>> 6c85f97630763fd1f55b75d67d815dac69d5a81d
    # ========================================================

    def rollback_agreement(self, operator_id, commit=True):
        """
<<<<<<< HEAD
        將公約內容還原至此版本的狀態。
        安全做法：修改 Agreement 內容後，必須呼叫 `save_version_snapshot` 生成新版本紀錄（如 v4 內容同 v2）。
=======
        直接用這個歷史版本覆蓋公約目前最新的內容。
        注意：這會觸發一輪新的「提案修改」，公約狀態會退回 pending 讓室友重新投票。
>>>>>>> 6c85f97630763fd1f55b75d67d815dac69d5a81d
        """
        from app.models.agreement import Agreement
        agreement = db.session.get(Agreement, self.agreement_id)
        if not agreement:
            raise ValueError("找不到關聯的公約本體，無法還原。")

<<<<<<< HEAD
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
=======
        # 把公約內容改回這一個版本的歷史文字
        agreement.title = self.title
        agreement.content = self.content_after
        agreement.status = 'pending'  # 退回待審核
        
        # 清除舊的投票紀錄（內容變了必須重新投票）
        agreement.approvals.delete()
>>>>>>> 6c85f97630763fd1f55b75d67d815dac69d5a81d
        
        if commit:
            db.session.commit()
        return agreement

<<<<<<< HEAD
    # ===== 基礎 CRUD 方法 =====
=======
    # ===== 基礎 CRUD 方法 (優化版) =====
>>>>>>> 6c85f97630763fd1f55b75d67d815dac69d5a81d

    @classmethod
    def get_by_id(cls, version_id):
        return db.session.get(cls, version_id)

    @classmethod
    def get_by_agreement(cls, agreement_id):
        """依據公約 ID 撈出所有的版本紀錄（新 -> 舊）"""
        return cls.query.filter_by(agreement_id=agreement_id)\
<<<<<<< HEAD
                         .order_by(cls.version_number.desc()).all()

    def delete(self, commit=True):
        """審計合規：歷史紀錄一般禁止單獨刪除"""
        raise NotImplementedError("為了維護公約變更的審計完整性，禁止單獨刪除歷史版本紀錄。")
=======
                        .order_by(cls.version_number.desc()).all()

    def delete(self, commit=True):
        """歷史紀錄一般不給刪，除非整組清掉"""
        db.session.delete(self)
        if commit:
            db.session.commit()
        return True
>>>>>>> 6c85f97630763fd1f55b75d67d815dac69d5a81d
