"""
儀表板路由 — 首頁總覽
Blueprint prefix: /dashboard
"""

from flask import Blueprint, render_template, redirect, url_for, g, flash
from app.routes.auth import login_required
from app.models.group import Group
from app.models.agreement import Agreement
from app.models import Notification, Chore

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('', methods=['GET'])
@login_required
def dashboard_page():
    """首頁儀表板"""
    user = g.user
    
    # 檢查是否已加入群組
    if not user['group_id']:
        flash("請先加入或建立群組！", "warning")
        return redirect(url_for('group.create_page'))
        
    try:
        # 1. 取得群組資訊
        group = Group.get_by_id(user['group_id'])
        
        # 2. 抓取該群組的公約
        agreements_active = Agreement.get_by_group(user['group_id'], status='active')
        agreements_pending = Agreement.get_by_group(user['group_id'], status='pending')
        
        # 3. 取得未讀通知
        notifications = Notification.get_unread_by_user(user['id'])
        
        # 4. 取得此使用者的待完成家事
        pending_chores = Chore.get_pending_by_user(user['id'])
        
        return render_template(
            'dashboard/index.html',
            group=group,
            agreements_active=agreements_active[:5],  # 最多顯示 5 筆
            agreements_pending=agreements_pending,
            notifications=notifications,
            pending_chores=pending_chores
        )
    except Exception as e:
        print(f"Error loading dashboard: {e}")
        return render_template(
            'dashboard/index.html',
            group=None,
            agreements_active=[],
            agreements_pending=[],
            notifications=[],
            pending_chores=[]
        )

@dashboard_bp.route('/home', methods=['GET'])
@login_required
def index():
    """別名路由，供與舊程式相容"""
    return redirect(url_for('dashboard.dashboard_page'))
