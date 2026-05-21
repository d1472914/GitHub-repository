import secrets
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import group as group_model
from app.models import user as user_model

group_bp = Blueprint('group', __name__, url_prefix='/group')

@group_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    # 若已有群組，直接導向設定頁
    if current_user.group_id:
        return redirect(url_for('group.settings'))
        
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash("群組名稱不能為空！", "danger")
            return render_template('group/create.html')
            
        # 產生不重複的 6 字元邀請碼
        invite_code = secrets.token_hex(3).upper()
        # 簡單確認重複
        while group_model.get_by_invite_code(invite_code) is not None:
            invite_code = secrets.token_hex(3).upper()
            
        try:
            group_id = group_model.create({
                'name': name,
                'invite_code': invite_code,
                'created_by': current_user.id
            })
            
            # 將目前使用者綁定到此群組
            user_model.update(current_user.id, {'group_id': group_id})
            current_user.group_id = group_id # 即時同步
            
            flash(f"成功建立群組「{name}」！邀請碼為：{invite_code}", "success")
            return redirect(url_for('group.settings'))
        except Exception as e:
            flash(f"建立群組失敗，資料庫錯誤：{e}", "danger")
            return render_template('group/create.html')
            
    return render_template('group/create.html')

@group_bp.route('/join', methods=['GET', 'POST'])
@login_required
def join():
    if current_user.group_id:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        invite_code = request.form.get('invite_code', '').strip().upper()
        if not invite_code:
            flash("請輸入邀請碼！", "danger")
            return render_template('group/join.html')
            
        db_group = group_model.get_by_invite_code(invite_code)
        if not db_group:
            flash("無效的邀請碼，找不到該群組！", "danger")
            return render_template('group/join.html')
            
        try:
            # 將使用者綁定到群組
            user_model.update(current_user.id, {'group_id': db_group['id']})
            current_user.group_id = db_group['id']
            
            flash(f"已成功加入群組「{db_group['name']}」！", "success")
            return redirect(url_for('dashboard.index'))
        except Exception as e:
            flash(f"加入群組失敗，資料庫錯誤：{e}", "danger")
            return render_template('group/join.html')
            
    return render_template('group/join.html')

@group_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if not current_user.group_id:
        return redirect(url_for('group.join'))
        
    db_group = group_model.get_by_id(current_user.group_id)
    if not db_group:
        flash("群組不存在！", "danger")
        return redirect(url_for('group.create'))
        
    # 取得群組內的所有成員
    all_users = user_model.get_all()
    members = [u for u in all_users if u['group_id'] == current_user.group_id]
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash("群組名稱不能為空！", "danger")
            return render_template('group/settings.html', group=db_group, members=members)
            
        try:
            group_model.update(db_group['id'], {'name': name})
            flash("群組名稱更新成功！", "success")
            return redirect(url_for('group.settings'))
        except Exception as e:
            flash(f"更新失敗，資料庫錯誤：{e}", "danger")
            return render_template('group/settings.html', group=db_group, members=members)
            
    return render_template('group/settings.html', group=db_group, members=members)
