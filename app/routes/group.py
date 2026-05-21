import random
import string
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.group import Group
from app.models.user import User

group_bp = Blueprint('group', __name__)

def generate_invite_code(length=6):
    """產生隨機唯一邀請碼"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if not Group.get_by_invite_code(code):
            return code

@group_bp.route('/')
@login_required
def group_home():
    """群組主頁 / 建立或加入群組"""
    if current_user.group_id:
        group = Group.get_by_id(current_user.group_id)
        if not group:
            # 防呆：如果資料庫的群組已被刪除但使用者 group_id 還在
            User.update(current_user.id, {'group_id': None, 'role': 'member'})
            return redirect(url_for('group.group_home'))
            
        members = User.get_by_group(current_user.group_id)
        is_admin = (group.created_by == current_user.id)
        return render_template('group/settings.html', group=group, members=members, is_admin=is_admin)
        
    return render_template('group/home.html')

@group_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_group():
    """建立群組"""
    if current_user.group_id:
        flash('您已經在一個群組中了！', 'warning')
        return redirect(url_for('group.group_home'))
        
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('群組名稱不能為空白！', 'warning')
            return render_template('group/create.html')
            
        invite_code = generate_invite_code()
        group_data = {
            'name': name,
            'invite_code': invite_code,
            'created_by': current_user.id
        }
        
        new_group = Group.create(group_data)
        if new_group:
            # 更新使用者為此群組的管理員
            User.update(current_user.id, {'group_id': new_group.id, 'role': 'admin'})
            flash(f'成功建立群組「{name}」！邀請碼為：{invite_code}', 'success')
            return redirect(url_for('group.group_home'))
        else:
            flash('建立群組失敗，請重試。', 'danger')
            
    return render_template('group/create.html')

@group_bp.route('/join', methods=['GET', 'POST'])
@login_required
def join_group():
    """加入群組"""
    if current_user.group_id:
        flash('您已經在一個群組中了！', 'warning')
        return redirect(url_for('group.group_home'))
        
    if request.method == 'POST':
        invite_code = request.form.get('invite_code', '').strip().upper()
        if not invite_code:
            flash('請輸入邀請碼！', 'warning')
            return render_template('group/join.html')
            
        group = Group.get_by_invite_code(invite_code)
        if group:
            # 加入群組，角色設為成員
            User.update(current_user.id, {'group_id': group.id, 'role': 'member'})
            flash(f'成功加入群組「{group.name}」！', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('無效的邀請碼，請確認後再試！', 'danger')
            return render_template('group/join.html', invite_code=invite_code)
            
    return render_template('group/join.html')

@group_bp.route('/leave', methods=['POST'])
@login_required
def leave_group():
    """離開群組"""
    if not current_user.group_id:
        flash('您不屬於任何群組！', 'warning')
        return redirect(url_for('group.group_home'))
        
    group = Group.get_by_id(current_user.group_id)
    if not group:
        User.update(current_user.id, {'group_id': None, 'role': 'member'})
        return redirect(url_for('group.group_home'))
        
    members = User.get_by_group(group.id)
    
    if len(members) == 1:
        # 如果是最後一個人，直接刪除群組
        # 為了安全起見，先將使用者移出群組，再刪除群組
        User.update(current_user.id, {'group_id': None, 'role': 'member'})
        Group.delete(group.id)
        flash('您已離開群組，該群組已因無成員而自動刪除。', 'info')
    else:
        # 如果還有其他成員
        if group.created_by == current_user.id:
            # 如果是管理員，必須先轉移管理員，或者隨機指派一個新的管理員
            # 這裡我們隨機挑選另一位成員作為新管理員
            new_admin = next(m for m in members if m.id != current_user.id)
            Group.update(group.id, {'created_by': new_admin.id})
            User.update(new_admin.id, {'role': 'admin'})
            
        User.update(current_user.id, {'group_id': None, 'role': 'member'})
        flash('您已成功離開群組！', 'info')
        
    return redirect(url_for('group.group_home'))

@group_bp.route('/update', methods=['POST'])
@login_required
def update_group():
    """更新群組名稱 (管理員權限)"""
    if not current_user.group_id:
        flash('操作無效！', 'danger')
        return redirect(url_for('group.group_home'))
        
    group = Group.get_by_id(current_user.group_id)
    if not group or group.created_by != current_user.id:
        flash('只有群組管理員才能更新設定！', 'danger')
        return redirect(url_for('group.group_home'))
        
    name = request.form.get('name', '').strip()
    if not name:
        flash('群組名稱不能為空白！', 'warning')
        return redirect(url_for('group.group_home'))
        
    Group.update(group.id, {'name': name})
    flash('群組名稱已更新！', 'success')
    return redirect(url_for('group.group_home'))
