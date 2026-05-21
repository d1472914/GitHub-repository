from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.utils.auth_helpers import group_required
from app.models import chore as chore_model
from app.models import user as user_model
from app.models import notification as noti_model

chore_bp = Blueprint('chore', __name__)

@chore_bp.route('/chores', methods=['GET'])
@login_required
@group_required
def list_chores():
    try:
        chores = chore_model.get_by_group(current_user.group_id)
        roommates = user_model.get_users_by_group(current_user.group_id)
        user_map = {r['id']: r['nickname'] for r in roommates}
        
        chore_displays = []
        for c in chores:
            chore_displays.append({
                'id': c['id'],
                'title': c['title'],
                'description': c['description'],
                'recurrence': c['recurrence'],
                'due_date': c['due_date'],
                'assigned_to_id': c['assigned_to'],
                'assigned_to_name': user_map.get(c['assigned_to'], '未知'),
                'status': c['status'],
                'created_by_name': user_map.get(c['created_by'], '未知'),
                'completed_at': c['completed_at']
            })
            
        return render_template('chore/list.html', chores=chore_displays)
    except Exception as e:
        flash(f"無法載入任務列表：{e}", "danger")
        return render_template('chore/list.html', chores=[])

@chore_bp.route('/chores/calendar', methods=['GET'])
@login_required
@group_required
def calendar():
    try:
        chores = chore_model.get_by_group(current_user.group_id)
        roommates = user_model.get_users_by_group(current_user.group_id)
        user_map = {r['id']: r['nickname'] for r in roommates}
        
        chore_displays = []
        for c in chores:
            chore_displays.append({
                'id': c['id'],
                'title': c['title'],
                'due_date': c['due_date'],
                'assigned_to_name': user_map.get(c['assigned_to'], '未知'),
                'status': c['status']
            })
            
        return render_template('chore/calendar.html', chores=chore_displays)
    except Exception as e:
        flash(f"無法載入日曆：{e}", "danger")
        return render_template('chore/calendar.html', chores=[])

@chore_bp.route('/chores/new', methods=['GET'])
@login_required
@group_required
def new_chore():
    try:
        roommates = user_model.get_users_by_group(current_user.group_id)
        return render_template('chore/form.html', chore=None, members=roommates)
    except Exception as e:
        flash(f"無法載入成員名單：{e}", "danger")
        return redirect(url_for('chore.list_chores'))

@chore_bp.route('/chores', methods=['POST'])
@login_required
@group_required
def create_chore():
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    recurrence = request.form.get('recurrence', 'once').strip()
    due_date = request.form.get('due_date', '').strip()
    assigned_to_str = request.form.get('assigned_to', '').strip()

    roommates = user_model.get_users_by_group(current_user.group_id)

    if not title or not due_date or not assigned_to_str:
        flash("任務名稱、到期日與指派對象為必填！", "danger")
        return render_template('chore/form.html', chore=None, members=roommates)

    try:
        assigned_to = int(assigned_to_str)
        chore_id = chore_model.create({
            'group_id': current_user.group_id,
            'title': title,
            'description': description or None,
            'recurrence': recurrence,
            'due_date': due_date,
            'assigned_to': assigned_to,
            'status': 'pending',
            'created_by': current_user.id
        })

        # 指派通知
        noti_model.create({
            'user_id': assigned_to,
            'group_id': current_user.group_id,
            'type': 'chore',
            'title': '您被指派了新的家事任務',
            'message': f'任務「{title}」已指派給您，請於 {due_date} 前完成！',
            'is_read': 0
        })

        flash("任務指派成功！已通知該名成員。", "success")
        return redirect(url_for('chore.list_chores'))
    except Exception as e:
        flash(f"任務建立失敗，資料庫錯誤：{e}", "danger")
        return render_template('chore/form.html', chore=None, members=roommates)

@chore_bp.route('/chores/<int:id>/edit', methods=['GET'])
@login_required
@group_required
def edit_chore(id):
    chore = chore_model.get_by_id(id)
    if not chore or chore['group_id'] != current_user.group_id:
        abort(404)
        
    try:
        roommates = user_model.get_users_by_group(current_user.group_id)
        return render_template('chore/form.html', chore=chore, members=roommates)
    except Exception as e:
        flash(f"無法載入編輯頁面：{e}", "danger")
        return redirect(url_for('chore.list_chores'))

@chore_bp.route('/chores/<int:id>/update', methods=['POST'])
@login_required
@group_required
def update_chore(id):
    chore = chore_model.get_by_id(id)
    if not chore or chore['group_id'] != current_user.group_id:
        abort(404)

    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    recurrence = request.form.get('recurrence', 'once').strip()
    due_date = request.form.get('due_date', '').strip()
    assigned_to_str = request.form.get('assigned_to', '').strip()

    roommates = user_model.get_users_by_group(current_user.group_id)

    if not title or not due_date or not assigned_to_str:
        flash("任務名稱、到期日與指派對象為必填！", "danger")
        return render_template('chore/form.html', chore=chore, members=roommates)

    try:
        assigned_to = int(assigned_to_str)
        old_assigned_to = chore['assigned_to']
        
        chore_model.update(id, {
            'title': title,
            'description': description or None,
            'recurrence': recurrence,
            'due_date': due_date,
            'assigned_to': assigned_to
        })

        # 指派對象若有變更，則發送通知
        if assigned_to != old_assigned_to:
            noti_model.create({
                'user_id': assigned_to,
                'group_id': current_user.group_id,
                'type': 'chore',
                'title': '您被指派了變更後的家事任務',
                'message': f'任務「{title}」指派對象已變更為您，請於 {due_date} 前完成！',
                'is_read': 0
            })

        flash("任務修改成功！", "success")
        return redirect(url_for('chore.list_chores'))
    except Exception as e:
        flash(f"修改失敗，資料庫錯誤：{e}", "danger")
        return render_template('chore/form.html', chore=chore, members=roommates)

@chore_bp.route('/chores/<int:id>/complete', methods=['POST'])
@login_required
@group_required
def complete_chore(id):
    chore = chore_model.get_by_id(id)
    if not chore or chore['group_id'] != current_user.group_id:
        abort(404)

    # 權限驗證：只有指派者(或當初指派對象本人)可以標記完成？
    # ROUTES.md 錯誤處理規定：「非負責人操作」報錯。說明只有任務負責人 (assigned_to) 才能完成
    if chore['assigned_to'] != current_user.id:
        flash("您非本任務的負責人，無法標記完成！", "danger")
        return redirect(url_for('chore.list_chores'))

    try:
        now_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        chore_model.update(id, {
            'status': 'completed',
            'completed_at': now_str
        })
        flash("恭喜！任務已標記為已完成。", "success")
        return redirect(url_for('chore.list_chores'))
    except Exception as e:
        flash(f"標記完成失敗：{e}", "danger")
        return redirect(url_for('chore.list_chores'))
