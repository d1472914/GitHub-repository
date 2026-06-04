"""
隱形管家路由 — 家事任務列表、視覺化日曆、新增任務、編輯任務、更新任務、完成任務
Blueprint prefix: /chores
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from app.routes.auth import login_required
from app.models import Chore, User

chore_bp = Blueprint('chore', __name__, url_prefix='/chores')

@chore_bp.route('', methods=['GET'])
@login_required
def list_page():
    """任務列表
    - 輸出：chore/list.html
    """
    group_id = g.user['group_id']
    if not group_id:
        flash("請先加入或建立群組！", "warning")
        return redirect(url_for('group.create_page'))

    try:
        chores = Chore.get_by_group_id(group_id)
        # ✅ 修正處：將 sqlite3.Row 轉為 dict，這樣後面才能順利使用 .get('nickname')
        members = {m['id']: dict(m) for m in User.get_by_group_id(group_id)}
        
        # 組裝暱稱
        chore_list = []
        for ch in chores:
            assignee_name = members.get(ch['assigned_to'], {}).get('nickname', '未分配')
            creator_name = members.get(ch['created_by'], {}).get('nickname', '系統')
            chore_list.append({
                'id': ch['id'],
                'title': ch['title'],
                'description': ch['description'],
                'recurrence': ch['recurrence'],
                'due_date': ch['due_date'],
                'assigned_to_name': assignee_name,
                'assigned_to': ch['assigned_to'],
                'status': ch['status'],
                'completed_at': ch['completed_at'],
                'creator_name': creator_name
            })
            
        return render_template('chore/list.html', chores=chore_list)
    except Exception as e:
        print(f"Error loading chores: {e}")
        flash("無法載入家事任務列表。", "error")
        return redirect(url_for('dashboard.index'))

@chore_bp.route('/calendar', methods=['GET'])
@login_required
def calendar():
    """輪值日曆
    - 輸出：chore/calendar.html
    """
    group_id = g.user['group_id']
    if not group_id:
        flash("請先加入或建立群組！", "warning")
        return redirect(url_for('group.create_page'))

    try:
        chores = Chore.get_by_group_id(group_id)
        # ✅ 修正處：這裡也同步將成員轉為 dict 防止日曆頁面報錯
        members = {m['id']: dict(m) for m in User.get_by_group_id(group_id)}
        
        # 組裝日曆事件
        chore_events = []
        for ch in chores:
            assignee_name = members.get(ch['assigned_to'], {}).get('nickname', '未分配')
            chore_events.append({
                'id': ch['id'],
                'title': f"{ch['title']} ({assignee_name})",
                'start': ch['due_date'],
                'color': '#10b981' if ch['status'] == 'completed' else '#3b82f6'
            })
            
        return render_template('chore/calendar.html', events=chore_events)
    except Exception as e:
        print(f"Error loading calendar events: {e}")
        flash("無法載入輪值日曆。", "error")
        return redirect(url_for('chore.list_page'))

@chore_bp.route('/new', methods=['GET'])
@login_required
def new_page():
    """新增任務頁面
    - 輸出：chore/form.html
    """
    group_id = g.user['group_id']
    if not group_id:
        flash("請先加入或建立群組！", "warning")
        return redirect(url_for('group.create_page'))

    try:
        members = User.get_by_group_id(group_id)
        return render_template('chore/form.html', members=members, chore=None)
    except Exception as e:
        print(f"Error loading chore form: {e}")
        flash("載入新增表單失敗。", "error")
        return redirect(url_for('chore.list_page'))

@chore_bp.route('', methods=['POST'])
@login_required
def create():
    """新增任務處理
    - 輸入：title, description, recurrence, due_date, assigned_to
    - 處理：Chore.create()
    - 輸出：重導向 /chores
    """
    group_id = g.user['group_id']
    if not group_id:
        flash("操作無效，您尚未加入群組！", "error")
        return redirect(url_for('dashboard.index'))

    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    recurrence = request.form.get('recurrence', 'once').strip()
    due_date = request.form.get('due_date', '').strip()
    assigned_to_str = request.form.get('assigned_to', '').strip()

    if not title or not due_date or not assigned_to_str:
        flash("任務名稱、截止日期與指派人為必填項目！", "error")
        members = User.get_by_group_id(group_id)
        return render_template('chore/form.html', members=members, chore=None)

    try:
        assigned_to = int(assigned_to_str)
        chore_id = Chore.create({
            'group_id': group_id,
            'title': title,
            'description': description,
            'recurrence': recurrence,
            'due_date': due_date,
            'assigned_to': assigned_to,
            'status': 'pending',
            'created_by': g.user['id']
        })

        if chore_id:
            flash("家事任務建立成功！", "success")
            return redirect(url_for('chore.list_page'))
        else:
            flash("家事建立失敗，請稍後再試。", "error")
            members = User.get_by_group_id(group_id)
            return render_template('chore/form.html', members=members, chore=None)

    except Exception as e:
        print(f"Error creating chore: {e}")
        flash("建立任務時發生伺服器錯誤。", "error")
        return redirect(url_for('chore.list_page'))

@chore_bp.route('/<int:chore_id>/edit', methods=['GET'])
@login_required
def edit_page(chore_id):
    """顯示編輯任務頁面
    - 輸出：chore/form.html
    """
    try:
        chore = Chore.get_by_id(chore_id)
        if not chore or chore['group_id'] != g.user['group_id']:
            flash("找不到該任務或您無權編輯！", "error")
            return redirect(url_for('chore.list_page'))

        members = User.get_by_group_id(g.user['group_id'])
        return render_template('chore/form.html', members=members, chore=chore)
    except Exception as e:
        print(f"Error loading chore edit page: {e}")
        flash("載入編輯頁面失敗。", "error")
        return redirect(url_for('chore.list_page'))

@chore_bp.route('/<int:chore_id>/update', methods=['POST'])
@login_required
def update(chore_id):
    """更新任務 (只接受 POST)
    - 輸入：title, description, recurrence, due_date, assigned_to
    - 處理：Chore.update()
    - 輸出：重導向 /chores
    """
    try:
        chore = Chore.get_by_id(chore_id)
        if not chore or chore['group_id'] != g.user['group_id']:
            flash("找不到該任務或無編輯權限！", "error")
            return redirect(url_for('chore.list_page'))

        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        recurrence = request.form.get('recurrence', 'once').strip()
        due_date = request.form.get('due_date', '').strip()
        assigned_to_str = request.form.get('assigned_to', '').strip()

        if not title or not due_date or not assigned_to_str:
            flash("任務名稱、截止日期與指派人為必填項目！", "error")
            members = User.get_by_group_id(g.user['group_id'])
            return render_template('chore/form.html', members=members, chore=chore)

        assigned_to = int(assigned_to_str)
        success = Chore.update(chore_id, {
            'title': title,
            'description': description,
            'recurrence': recurrence,
            'due_date': due_date,
            'assigned_to': assigned_to
        })

        if success:
            flash("任務更新成功！", "success")
        else:
            flash("任務無實質變更或更新失敗。", "info")
            
        return redirect(url_for('chore.list_page'))

    except Exception as e:
        print(f"Error updating chore: {e}")
        flash("更新任務時發生伺服器錯誤。", "error")
        return redirect(url_for('chore.list_page'))

@chore_bp.route('/<int:chore_id>/complete', methods=['POST'])
@login_required
def complete(chore_id):
    """完成任務 (只接受 POST)
    - 處理：Chore.mark_completed()
    - 輸出：重導向 /chores
    """
    try:
        chore = Chore.get_by_id(chore_id)
        if not chore or chore['group_id'] != g.user['group_id']:
            flash("該任務不存在！", "error")
            return redirect(url_for('chore.list_page'))

        # 檢查是否為負責人
        if chore['assigned_to'] != g.user['id']:
            flash("操作失敗！您不是該家事任務的負責人！", "error")
            return redirect(url_for('chore.list_page'))

        success = Chore.mark_completed(chore_id)
        if success:
            flash(f"太棒了！任務「{chore['title']}」已順利完成！", "success")
        else:
            flash("標記完成失敗，請稍後再試。", "error")

        return redirect(url_for('chore.list_page'))

    except Exception as e:
        print(f"Error completing chore: {e}")
        flash("標記完成時發生伺服器錯誤。", "error")
        return redirect(url_for('chore.list_page'))