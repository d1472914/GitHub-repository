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
