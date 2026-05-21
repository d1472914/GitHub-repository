from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.agreement import Agreement
from app.models.group import Group

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('', methods=['GET'])
@login_required
def dashboard_page():
    """首頁儀表板"""
    if not current_user.group_id:
        flash('請先建立或加入一個房間群組。', 'info')
        return redirect(url_for('group.create_page'))
        
    group = Group.get_by_id(current_user.group_id)
    
    # 抓取該群組的公約
    agreements_active = Agreement.get_by_group(current_user.group_id, status='active')
    agreements_pending = Agreement.get_by_group(current_user.group_id, status='pending')
    
    return render_template(
        'dashboard/index.html',
        group=group,
        agreements_active=agreements_active[:5],  # 最多顯示 5 筆
        agreements_pending=agreements_pending
    )
