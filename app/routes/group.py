"""
群組管理路由 — 建立、加入、設定
Blueprint prefix: /group
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash

group_bp = Blueprint('group', __name__, url_prefix='/group')


@group_bp.route('/create', methods=['GET'])
def create_page():
    """顯示建立群組表單
    - 輸出：group/create.html
    """
    pass


@group_bp.route('/create', methods=['POST'])
def create():
    """處理建立群組
    - 輸入：name
    - 處理：產生邀請碼 → Group.create() → 更新 user.group_id → user.role='admin'
    - 輸出：重導向 /group/settings
    """
    pass


@group_bp.route('/join', methods=['GET'])
def join_page():
    """顯示加入群組表單
    - 輸出：group/join.html
    """
    pass


@group_bp.route('/join', methods=['POST'])
def join():
    """處理加入群組
    - 輸入：invite_code
    - 處理：Group.get_by_invite_code() → 更新 user.group_id
    - 輸出：成功 → 重導向 /dashboard；失敗 → 回到加入頁
    """
    pass


@group_bp.route('/settings', methods=['GET'])
def settings_page():
    """顯示群組設定頁面
    - 輸出：group/settings.html（群組資訊、成員列表、邀請碼）
    """
    pass


@group_bp.route('/settings', methods=['POST'])
def settings_update():
    """更新群組設定
    - 輸入：name（群組名稱）
    - 處理：group.update()
    - 輸出：重導向 /group/settings
    """
    pass
