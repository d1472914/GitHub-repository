<<<<<<< HEAD
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
=======
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import notification as noti_model
from app.models import chore as chore_model
from app.models import group as group_model

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    # 若未加入群組，重導向加入或建立群組頁面
    if not current_user.group_id:
        flash("您尚未加入任何寢室或租屋群組，請先建立或加入一個！", "info")
        return redirect(url_for('group.create'))
        
    try:
        # 取得未讀通知
        unread_notifications = noti_model.get_unread_by_user(current_user.id)
        
        # 取得待辦任務
        all_chores = chore_model.get_all()
        pending_chores = [
            c for c in all_chores 
            if c['assigned_to'] == current_user.id and c['status'] == 'pending'
        ]
        
        # 取得群組資訊
        group_info = group_model.get_by_id(current_user.group_id)
        
        return render_template(
            'dashboard/index.html',
            notifications=unread_notifications,
            chores=pending_chores,
            group=group_info
        )
    except Exception as e:
        flash(f"載入儀表板時發生錯誤：{e}", "danger")
        return render_template('dashboard/index.html', notifications=[], chores=[], group=None)
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
