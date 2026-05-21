from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.utils.auth_helpers import group_required
from app.models.chore import Chore
from app.models.user import User
from app.models.notification import Notification

chore_bp = Blueprint('chore', __name__)

@chore_bp.route('/')
@login_required
@group_required
def list_chores():
    """家事任務列表"""
    chores = Chore.get_by_group(current_user.group_id)
    members = User.get_by_group(current_user.group_id)
    members_dict = {m.id: m for m in members}
    
    chores_data = []
    for c in chores:
        assignee = members_dict.get(c.assigned_to)
        creator = members_dict.get(c.created_by)
        
        # 轉換 due_date 方便前端顯示
        due_date_obj = datetime.strptime(c.due_date, '%Y-%m-%d') if isinstance(c.due_date, str) else c.due_date
        
        # 判斷是否逾期
        is_overdue = (c.status == 'pending' and due_date_obj.date() < datetime.now().date())
        
        chores_data.append({
            'info': c,
            'assignee_name': assignee.nickname if assignee else '未指派',
            'creator_name': creator.nickname if creator else '系統',
            'is_overdue': is_overdue
        })
        
    return render_template('chore/list.html', chores=chores_data)

@chore_bp.route('/new', methods=['GET', 'POST'])
@login_required
@group_required
def create_chore():
    """建立家事任務"""
    members = User.get_by_group(current_user.group_id)
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        recurrence = request.form.get('recurrence', 'once').strip()
        due_date = request.form.get('due_date', '').strip()
        assigned_to_id = request.form.get('assigned_to', type=int)
        
        if not title or not due_date or not assigned_to_id:
            flash('請填寫任務標題、到期日與指派對象！', 'warning')
            return render_template('chore/form.html', members=members, title=title, description=description, due_date=due_date)
            
        chore_data = {
            'group_id': current_user.group_id,
            'title': title,
            'description': description,
            'recurrence': recurrence,
            'due_date': due_date,
            'assigned_to': assigned_to_id,
            'status': 'pending',
            'created_by': current_user.id
        }
        
        new_chore = Chore.create(chore_data)
        if new_chore:
            # 發送通知給被指派人 (排除自己指派給自己)
            if assigned_to_id != current_user.id:
                assignee = next((m for m in members if m.id == assigned_to_id), None)
                if assignee:
                    Notification.create({
                        'user_id': assigned_to_id,
                        'group_id': current_user.group_id,
                        'type': 'chore',
                        'title': '被指派新家事任務',
                        'message': f'室友 {current_user.nickname} 指派了一項家事任務給您：「{title}」，請在 {due_date} 前完成。'
                    })
                    
            flash('家事任務建立並指派成功！', 'success')
            return redirect(url_for('chore.list_chores'))
        else:
            flash('建立任務失敗，請重試。', 'danger')
            
    return render_template('chore/form.html', members=members)

@chore_bp.route('/<int:chore_id>/complete', methods=['POST'])
@login_required
@group_required
def complete_chore(chore_id):
    """標記家事任務為已完成"""
    chore = Chore.get_by_id(chore_id)
    if not chore or chore.group_id != current_user.group_id:
        flash('找不到該家事任務！', 'danger')
        return redirect(url_for('chore.list_chores'))
        
    if chore.assigned_to != current_user.id and current_user.role != 'admin':
        flash('只有該任務的指派人或群組管理員才能標記完成！', 'danger')
        return redirect(url_for('chore.list_chores'))
        
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    Chore.update(chore_id, {
        'status': 'completed',
        'completed_at': now_str
    })
    
    # 建立週期性任務的下一期任務 (若是循環任務)
    if chore.recurrence != 'once':
        try:
            due_date_obj = datetime.strptime(chore.due_date, '%Y-%m-%d')
        except ValueError:
            due_date_obj = datetime.now()
            
        import datetime as dt
        if chore.recurrence == 'daily':
            next_due = due_date_obj + dt.timedelta(days=1)
        elif chore.recurrence == 'weekly':
            next_due = due_date_obj + dt.timedelta(weeks=1)
        elif chore.recurrence == 'monthly':
            # 約略加 30 天，或下個月同日
            next_due = due_date_obj + dt.timedelta(days=30)
            
        Chore.create({
            'group_id': chore.group_id,
            'title': chore.title,
            'description': chore.description,
            'recurrence': chore.recurrence,
            'due_date': next_due.strftime('%Y-%m-%d'),
            'assigned_to': chore.assigned_to,
            'status': 'pending',
            'created_by': current_user.id
        })
        
    # 通知建立者與群組內其他室友
    members = User.get_by_group(current_user.group_id)
    for m in members:
        if m.id != current_user.id:
            Notification.create({
                'user_id': m.id,
                'group_id': current_user.group_id,
                'type': 'chore',
                'title': '家事任務已完成',
                'message': f'室友 {current_user.nickname} 已完成了家事任務：「{chore.title}」。'
            })
            
    flash('已標記任務為已完成！', 'success')
    return redirect(url_for('chore.list_chores'))

@chore_bp.route('/<int:chore_id>/delete', methods=['POST'])
@login_required
@group_required
def delete_chore(chore_id):
    """刪除家事任務"""
    chore = Chore.get_by_id(chore_id)
    if not chore or chore.group_id != current_user.group_id:
        flash('找不到該家事任務！', 'danger')
        return redirect(url_for('chore.list_chores'))
        
    if chore.created_by != current_user.id and current_user.role != 'admin':
        flash('只有任務建立者或群組管理員才能刪除此任務！', 'danger')
        return redirect(url_for('chore.list_chores'))
        
    if Chore.delete(chore_id):
        flash('家事任務已成功刪除！', 'info')
    else:
        flash('刪除任務失敗，請重試。', 'danger')
        
    return redirect(url_for('chore.list_chores'))

@chore_bp.route('/calendar')
@login_required
@group_required
def calendar_view():
    """值日生排班日曆視角"""
    chores = Chore.get_by_group(current_user.group_id)
    members = User.get_by_group(current_user.group_id)
    members_dict = {m.id: m for m in members}
    
    # 將任務依日期分組
    calendar_data = {}
    for c in chores:
        due_date = c.due_date
        assignee = members_dict.get(c.assigned_to)
        
        if due_date not in calendar_data:
            calendar_data[due_date] = []
            
        calendar_data[due_date].append({
            'info': c,
            'assignee_nickname': assignee.nickname if assignee else '未指派'
        })
        
    # 依日期排序
    sorted_calendar = sorted(calendar_data.items())
    
    return render_template('chore/calendar.html', calendar=sorted_calendar)
