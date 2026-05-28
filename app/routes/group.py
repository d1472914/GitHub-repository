"""
群組管理路由 — 建立群組、加入群組、群組設定
Blueprint prefix: /group
"""

import secrets
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, session
from app.routes.auth import login_required
from app.models import Group, User

group_bp = Blueprint('group', __name__, url_prefix='/group')

@group_bp.route('/create', methods=['GET'])
@login_required
def create_page():
    """顯示建立群組表單頁面
    - 輸出：group/create.html
    """
    return render_template('group/create.html')

@group_bp.route('/create', methods=['POST'])
@login_required
def create():
    """建立群組處理
    - 輸入：name (群組名稱)
    - 處理：產生隨機邀請碼 → Group.create() → 更新 User.group_id
    - 輸出：重導向 /group/settings
    """
    name = request.form.get('name', '').strip()
    if not name:
        flash("群組名稱不可為空！", "error")
        return render_template('group/create.html')

    try:
        # 產生 8 碼大寫英數隨機邀請碼
        invite_code = secrets.token_hex(4).upper()
        
        group_data = {
            'name': name,
            'invite_code': invite_code,
            'created_by': g.user['id']
        }
        
        group_id = Group.create(group_data)
        if group_id:
            # 更新建立者的 group_id 與角色為 admin
            User.update(g.user['id'], {'group_id': group_id, 'role': 'admin'})
            # 重新整理快取在 g 裡的使用者資料
            g.user = User.get_by_id(g.user['id'])
            
            flash(f"群組「{name}」建立成功！邀請碼為：{invite_code}", "success")
            return redirect(url_for('group.settings_page'))
        else:
            flash("群組建立失敗，請稍後再試。", "error")
            return render_template('group/create.html')
            
    except Exception as e:
        print(f"Error creating group: {e}")
        flash("伺服器錯誤，請稍後再試。", "error")
        return render_template('group/create.html')

@group_bp.route('/join', methods=['GET'])
@login_required
def join_page():
    """顯示加入群組表單頁面
    - 輸出：group/join.html
    """
    return render_template('group/join.html')

@group_bp.route('/join', methods=['POST'])
@login_required
def join():
    """加入群組處理
    - 輸入：invite_code (邀請碼)
    - 處理：Group.get_by_invite_code() → 更新 User.group_id
    - 輸出：重導向 /dashboard
    """
    invite_code = request.form.get('invite_code', '').strip().upper()
    if not invite_code:
        flash("邀請碼不可為空！", "error")
        return render_template('group/join.html')

    try:
        # 尋找對應的群組
        group = Group.get_by_invite_code(invite_code)
        if not group:
            flash("無效的邀請碼，找不到該群組！", "error")
            return render_template('group/join.html')

        # 更新使用者的 group_id，加入群組
        User.update(g.user['id'], {'group_id': group['id'], 'role': 'member'})
        # 重新整理 g 裡的使用者資料
        g.user = User.get_by_id(g.user['id'])
        
        flash(f"成功加入群組「{group['name']}」！", "success")
        return redirect(url_for('dashboard.index'))
        
    except Exception as e:
        print(f"Error joining group: {e}")
        flash("伺服器錯誤，請稍後再試。", "error")
        return render_template('group/join.html')

@group_bp.route('/settings', methods=['GET'])
@login_required
def settings_page():
    """群組設定頁面
    - 輸出：group/settings.html (含群組成員列表與邀請碼)
    """
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
        return redirect(url_for('dashboard.index'))

@group_bp.route('/settings', methods=['POST'])
@login_required
def update_settings():
    """更新群組設定
    - 輸入：name (新群組名稱)
    - 處理：Group.update()
    - 輸出：重導向 /group/settings
    """
    name = request.form.get('name', '').strip()
    if not name:
        flash("群組名稱不可為空！", "error")
        return redirect(url_for('group.settings_page'))

    try:
        group_id = g.user['group_id']
        if not group_id:
            flash("操作無效！您不屬於任何群組。", "error")
            return redirect(url_for('dashboard.index'))

        success = Group.update(group_id, {'name': name})
        if success:
            flash("群組設定更新成功！", "success")
        else:
            flash("更新失敗，請檢查資料是否正確。", "error")
            
        return redirect(url_for('group.settings_page'))
        
    except Exception as e:
        print(f"Error updating group settings: {e}")
        flash("伺服器錯誤，更新失敗。", "error")
        return redirect(url_for('group.settings_page'))
