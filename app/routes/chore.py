"""
隱形管家路由 — 任務排班、輪值日曆、完成確認
Blueprint prefix: /chores
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash

chore_bp = Blueprint('chore', __name__, url_prefix='/chores')


@chore_bp.route('', methods=['GET'])
def list_chores():
    """任務列表
    - 處理：Chore.get_by_group(current_user.group_id)
    - 輸出：chore/list.html
    """
    pass


@chore_bp.route('/calendar', methods=['GET'])
def calendar():
    """輪值日曆
    - 處理：取得群組所有任務，依日期組織
    - 輸出：chore/calendar.html
    """
    pass


@chore_bp.route('/new', methods=['GET'])
def new_page():
    """新增任務頁面
    - 輸出：chore/form.html（空白表單，mode='create'，含成員下拉選單）
    """
    pass


@chore_bp.route('', methods=['POST'])
def create():
    """新增任務處理
    - 輸入：title, description, recurrence, due_date, assigned_to
    - 處理：Chore.create() → Notification.create() 通知負責人
    - 輸出：重導向 /chores
    """
    pass


@chore_bp.route('/<int:id>/edit', methods=['GET'])
def edit_page(id):
    """編輯任務頁面
    - 輸入：URL 參數 id
    - 輸出：chore/form.html（預填資料，mode='edit'）
    - 錯誤：不存在 → 404
    """
    pass


@chore_bp.route('/<int:id>/update', methods=['POST'])
def update(id):
    """更新任務
    - 輸入：URL 參數 id；表單 title, description, recurrence, due_date, assigned_to
    - 處理：chore.update()
    - 輸出：重導向 /chores
    - 錯誤：不存在 → 404
    """
    pass


@chore_bp.route('/<int:id>/complete', methods=['POST'])
def complete(id):
    """完成任務
    - 輸入：URL 參數 id
    - 處理：Chore.get_by_id() → chore.mark_completed()
    - 輸出：重導向 /chores
    - 錯誤：不存在 → 404；非負責人 → 403
    """
    pass
