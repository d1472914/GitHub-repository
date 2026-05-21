import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.group import Group
from app.models.user import User
from app.models import db

group_bp = Blueprint('group', __name__, url_prefix='/group')


@group_bp.route('/create', methods=['GET'])
@login_required
def create_page():
    """顯示建立群組表單"""
    if current_user.group_id:
        flash('您已經加入了一個群組，無法重複建立。', 'warning')
        return redirect(url_for('dashboard.dashboard_page'))
    return render_template('group/create.html')


@group_bp.route('/create', methods=['POST'])
@login_required
def create():
    """處理建立群組"""
    name = request.form.get('name')
    if not name:
        flash('請輸入群組名稱。', 'danger')
        return redirect(url_for('group.create_page'))

    # 產生唯一的 6 碼大寫邀請碼
    invite_code = uuid.uuid4().hex[:6].upper()
    while Group.get_by_invite_code(invite_code):
        invite_code = uuid.uuid4().hex[:6].upper()

    # 建立群組
    group = Group.create(name=name, invite_code=invite_code, created_by=current_user.id)
    
    # 將創立者加入群組並將 role 設為 admin
    current_user.update(group_id=group.id, role='admin')
    
    flash(f'群組「{name}」建立成功！邀請碼為：{invite_code}', 'success')
    return redirect(url_for('group.settings_page'))


@group_bp.route('/join', methods=['GET'])
@login_required
def join_page():
    """顯示加入群組表單"""
    if current_user.group_id:
        flash('您已經加入了一個群組。', 'warning')
        return redirect(url_for('dashboard.dashboard_page'))
    return render_template('group/join.html')


@group_bp.route('/join', methods=['POST'])
@login_required
def join():
    """處理加入群組"""
    invite_code = request.form.get('invite_code')
    if not invite_code:
        flash('請輸入邀請碼。', 'danger')
        return redirect(url_for('group.join_page'))

    invite_code = invite_code.strip().upper()
    group = Group.get_by_invite_code(invite_code)
    if not group:
        flash('找不到該邀請碼對應的群組。', 'danger')
        return redirect(url_for('group.join_page'))

    # 更新使用者群組 ID
    current_user.update(group_id=group.id, role='member')
    flash(f'成功加入群組「{group.name}」！', 'success')
    return redirect(url_for('dashboard.dashboard_page'))


@group_bp.route('/settings', methods=['GET'])
@login_required
def settings_page():
    """顯示群組設定頁面"""
    if not current_user.group_id:
        flash('您尚未加入任何群組。', 'warning')
        return redirect(url_for('group.join_page'))
        
    group = Group.get_by_id(current_user.group_id)
    return render_template('group/settings.html', group=group)


@group_bp.route('/settings', methods=['POST'])
@login_required
def settings_update():
    """更新群組設定"""
    if not current_user.group_id:
        return redirect(url_for('dashboard.dashboard_page'))
        
    if current_user.role != 'admin':
        flash('只有管理員才能修改群組設定。', 'danger')
        return redirect(url_for('group.settings_page'))

    name = request.form.get('name')
    if not name:
        flash('群組名稱不能為空。', 'danger')
        return redirect(url_for('group.settings_page'))

    group = Group.get_by_id(current_user.group_id)
    group.update(name=name)
    flash('群組設定已成功更新。', 'success')
    return redirect(url_for('group.settings_page'))
