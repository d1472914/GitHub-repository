"""
儀表板路由 — 首頁總覽
Blueprint prefix: /dashboard
"""

from flask import Blueprint, render_template, redirect, url_for, g, session
from app.routes.auth import login_required
from app.models import Notification, Chore, Group

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('', methods=['GET'])
@login_required
def index():
    """首頁儀表板
    - 處理：取得未讀通知、待辦任務、群組資訊
    - 輸出：dashboard/index.html
    - 錯誤：未登入 → 重導向登入頁；未加入群組 → 重導向建立群組頁
    """
    user = g.user
    
    # 檢查是否已加入群組
    if not user['group_id']:
        return redirect(url_for('group.create_page'))
        
    try:
        # 1. 取得未讀通知
        notifications = Notification.get_unread_by_user(user['id'])
        
        # 2. 取得此使用者的待完成家事
        pending_chores = Chore.get_pending_by_user(user['id'])
        
        # 3. 取得群組資訊
        group = Group.get_by_id(user['group_id'])
        
        return render_template(
            'dashboard/index.html',
            notifications=notifications,
            pending_chores=pending_chores,
            group=group
        )
    except Exception as e:
        print(f"Error loading dashboard: {e}")
        return render_template('dashboard/index.html', notifications=[], pending_chores=[], group=None)
