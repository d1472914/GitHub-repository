"""
公約異動記錄路由 — 公約 CRUD、版本歷史、同意機制
Blueprint prefix: /agreements
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash

agreement_bp = Blueprint('agreement', __name__, url_prefix='/agreements')


@agreement_bp.route('', methods=['GET'])
def list_agreements():
    """公約列表
    - 處理：Agreement.get_by_group(current_user.group_id)
    - 輸出：agreement/list.html
    """
    pass


@agreement_bp.route('/new', methods=['GET'])
def new_page():
    """新增公約頁面
    - 輸出：agreement/form.html（空白表單，mode='create'）
    """
    pass


@agreement_bp.route('', methods=['POST'])
def create():
    """新增公約處理
    - 輸入：title, category, content
    - 處理：Agreement.create() → AgreementVersion.create(v1) → AgreementApproval.create()（提案者自動同意）
    - 輸出：重導向 /agreements/<id>
    """
    pass


@agreement_bp.route('/<int:id>', methods=['GET'])
def detail(id):
    """公約詳情
    - 輸入：URL 參數 id
    - 處理：Agreement.get_by_id() → 取得版本歷史與同意狀態
    - 輸出：agreement/detail.html
    - 錯誤：不存在 → 404
    """
    pass


@agreement_bp.route('/<int:id>/edit', methods=['GET'])
def edit_page(id):
    """編輯公約頁面
    - 輸入：URL 參數 id
    - 輸出：agreement/form.html（預填資料，mode='edit'）
    - 錯誤：不存在 → 404
    """
    pass


@agreement_bp.route('/<int:id>/update', methods=['POST'])
def update(id):
    """更新公約
    - 輸入：URL 參數 id；表單 title, category, content
    - 處理：記錄舊內容 → AgreementVersion.create() → agreement.update() → 重設同意
    - 輸出：重導向 /agreements/<id>
    - 錯誤：不存在 → 404
    """
    pass


@agreement_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """刪除公約
    - 輸入：URL 參數 id
    - 處理：Agreement.get_by_id() → agreement.delete()
    - 輸出：重導向 /agreements
    - 錯誤：不存在 → 404
    """
    pass


@agreement_bp.route('/<int:id>/approve', methods=['POST'])
def approve(id):
    """同意公約
    - 輸入：URL 參數 id
    - 處理：檢查未同意 → AgreementApproval.create() → 檢查全數通過 → 更新 status
    - 輸出：重導向 /agreements/<id>
    - 錯誤：不存在 → 404；已同意 → 忽略
    """
    pass
