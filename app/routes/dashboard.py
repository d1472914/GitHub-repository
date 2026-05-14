"""
儀表板路由 — 首頁總覽
Blueprint prefix: /dashboard
"""

from flask import Blueprint, render_template

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('', methods=['GET'])
def index():
    """首頁儀表板
    - 處理：取得未讀通知、待辦任務、群組資訊
    - 輸出：dashboard/index.html
    - 錯誤：未登入 → 重導向登入頁；未加入群組 → 重導向建立群組頁
    """
    pass
