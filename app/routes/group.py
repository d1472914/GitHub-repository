"""
群組管理路由 — 建立群組、加入群組、群組設定
Blueprint prefix: /group
"""

import secrets
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from app.routes.auth import login_required
from app.models.group import Group
from app.models.user import User

group_bp = Blueprint('group', __name__, url_prefix='/group')

@group_bp.route('/create', methods=['GET'])
@login_required
def create_page():
    """顯示建立群組表單"""
    if g.user['group_id']:
        flash('您已經加入或建立了一個群組，無法重複建立。', 'warning')
        return redirect(url_for('dashboard.dashboard_page'))
    return render_template('group/create.html')

@group_bp.route('/create', methods=['POST'])
@login_required
def create():
    """處理建立群組"""
    name = request.form.get('name', '').strip()
    if not name:
        flash("群組名稱不可為空！", "error")
        return redirect(url_for('group.create_page'))

    try:
        if g.user['group_id']:
            flash('您已經加入或建立了一個群組，無法重複建立。', 'warning')
            return redirect(url_for('dashboard.dashboard_page'))

        # 產生 8 碼大寫英數隨機邀請碼
        invite_code = secrets.token_hex(4).upper()
        
        group = Group.create(
            name=name,
            invite_code=invite_code,
            created_by=g.user['id']
        )
        
        if group:
            # 更新建立者的 group_id 與角色為 admin
            user = User.get_by_id(g.user['id'])
            user.update(group_id=group.id, role='admin')
            g.user = user
            
            flash(f"群組「{name}」建立成功！邀請碼為：{invite_code}", "success")
            return redirect(url_for('group.settings_page'))
        else:
            flash("群組建立失敗，請稍後再試。", "error")
            return redirect(url_for('group.create_page'))
            
    except Exception as e:
        print(f"Error creating group: {e}")
        flash("伺服器錯誤，請稍後再試。", "error")
        return redirect(url_for('group.create_page'))

@group_bp.route('/join', methods=['GET'])
@login_required
def join_page():
    """顯示加入群組表單"""
    if g.user['group_id']:
        flash('您已經加入了一個群組。', 'warning')
        return redirect(url_for('dashboard.dashboard_page'))
    return render_template('group/join.html')

@group_bp.route('/join', methods=['POST'])
@login_required
def join():
    """處理加入群組"""
    invite_code = request.form.get('invite_code', '').strip().upper()
    if not invite_code:
        flash("邀請碼不可為空！", "error")
        return redirect(url_for('group.join_page'))

    try:
        if g.user['group_id']:
            flash('您已經加入了一個群組。', 'warning')
            return redirect(url_for('dashboard.dashboard_page'))

        group = Group.get_by_invite_code(invite_code)
        if not group:
            flash("無效的邀請碼，找不到該群組！", "error")
            return redirect(url_for('group.join_page'))

        # 更新使用者的 group_id，加入群組
        user = User.get_by_id(g.user['id'])
        user.update(group_id=group.id, role='member')
        g.user = user
        
        flash(f"成功加入群組「{group.name}」！", "success")
        return redirect(url_for('dashboard.dashboard_page'))
        
    except Exception as e:
        print(f"Error joining group: {e}")
        flash("伺服器錯誤，請稍後再試。", "error")
        return redirect(url_for('group.join_page'))

@group_bp.route('/settings', methods=['GET'])
@login_required
def settings():
    """群組設定頁面"""
    if not g.user['group_id']:
        flash("您尚未加入或建立任何群組！", "warning")
        return redirect(url_for('group.create_page'))

    try:
        group = Group.get_by_id(g.user['group_id'])
        members = User.get_by_group_id(g.user['group_id'])
        return render_template('group/settings.html', group=group, members=members)
    except Exception as e:
        print(f"Error getting group settings: {e}")
        flash("無法取得群組設定資訊。", "error")
        return redirect(url_for('dashboard.dashboard_page'))

@group_bp.route('/settings_page', methods=['GET'])
@login_required
def settings_page():
    """相容性別名路由"""
    return settings()

@group_bp.route('/settings', methods=['POST'])
@login_required
def settings_update():
    """更新群組設定"""
    if not g.user['group_id']:
        return redirect(url_for('dashboard.dashboard_page'))
        
    if g.user['role'] != 'admin':
        flash('只有管理員才能修改群組設定。', 'danger')
        return redirect(url_for('group.settings_page'))

    name = request.form.get('name', '').strip()
    if not name:
        flash("群組名稱不可為空！", "error")
        return redirect(url_for('group.settings_page'))

    try:
        group = Group.get_by_id(g.user['group_id'])
        group.update(name=name)
        flash("群組設定更新成功！", "success")
        return redirect(url_for('group.settings_page'))
    except Exception as e:
        print(f"Error updating group settings: {e}")
        flash("伺服器錯誤，更新失敗。", "error")
        return redirect(url_for('group.settings_page'))

@group_bp.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    """相容於舊路由命名的別名端點"""
    return settings_update()
