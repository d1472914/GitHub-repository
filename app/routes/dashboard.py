from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.group import Group
from app.models.chore import Chore
from app.models.notification import Notification
from app.models.inventory_item import InventoryItem

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    """首頁儀表板"""
    if not current_user.group_id:
        return redirect(url_for('group.group_home'))
        
    group = Group.get_by_id(current_user.group_id)
    notifications = Notification.get_unread_by_user(current_user.id)
    pending_chores = Chore.get_pending_by_user(current_user.id)
    
    # 獲取低庫存物資
    all_items = InventoryItem.get_by_group(current_user.group_id)
    low_stock_items = [item for item in all_items if item.is_low_stock]
    
    return render_template(
        'dashboard/index.html',
        group=group,
        notifications=notifications,
        pending_chores=pending_chores,
        low_stock_items=low_stock_items
    )

@dashboard_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def read_all_notifications():
    """一鍵已讀所有通知"""
    Notification.mark_all_as_read(current_user.id)
    return redirect(url_for('dashboard.index'))
