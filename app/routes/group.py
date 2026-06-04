"""
群組管理路由 — 建立群組、加入群組、群組設定
Blueprint prefix: /group
"""

import secrets
from flask import Blueprint, render_template, request, redirect, url_for, flash, g, session
from werkzeug.security import generate_password_hash
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
    
@group_bp.route('/add_member', methods=['POST'])
@login_required
def add_member():
    """處理加入群組的請求，若使用者不存在則新增使用者並設定預設密碼"""
    group_id = g.user['group_id']
    if not group_id:
        flash("您尚未加入或建立任何群組！", "warning")
        return redirect(url_for('group.create_page'))

    nickname = request.form.get('nickname', '').strip()
    email = request.form.get('email', '').strip()

    if not nickname:
        flash("室友暱稱不可為空！", "error")
        return redirect(url_for('group.settings_page'))

    # 若未提供電子信箱，自動產生一個唯一的 placeholder 信箱
    if not email:
        email = f"user_{secrets.token_hex(4)}@example.com"

    try:
        # 檢查該電子信箱是否已存在
        existing_user = User.get_by_email(email)
        if existing_user:
            if existing_user['group_id'] == group_id:
                flash(f"使用者「{existing_user['nickname']}」已在群組中！", "info")
            elif existing_user['group_id']:
                flash("此電子信箱已被其他群組成員使用！", "error")
            else:
                # 使用者存在但沒有群組，直接將其加入目前群組
                User.update(existing_user['id'], {'group_id': group_id, 'role': 'member'})
                flash(f"已將現有使用者「{existing_user['nickname']}」加入群組！", "success")
        else:
            # 建立新使用者並設定預設密碼
            hashed_password = generate_password_hash("123456")
            user_data = {
                'email': email,
                'password_hash': hashed_password,
                'nickname': nickname,
                'role': 'member',
                'group_id': group_id
            }
            new_user_id = User.create(user_data)
            if new_user_id:
                flash(f"成功新增室友「{nickname}」，預設密碼為 123456", "success")
            else:
                flash("新增室友失敗，請稍後再試。", "error")

    except Exception as e:
        print(f"Error adding roommate: {e}")
        flash("伺服器錯誤，新增室友失敗。", "error")

    return redirect(url_for('group.settings_page'))