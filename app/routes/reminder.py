from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.utils.auth_helpers import group_required
from app.models import reminder as reminder_model
from app.models import user as user_model
from app.models import group as group_model
from app.models import notification as noti_model

reminder_bp = Blueprint('reminder', __name__)

# 中英文分類名稱對照
CATEGORY_NAMES = {
    'noise': '噪音管理',
    'hygiene': '衛生清潔',
    'other': '其他約定'
}

@reminder_bp.route('/reminders/send', methods=['GET'])
@login_required
@group_required
def send_form():
    try:
        # 取得群組內除了當前使用者之外的所有成員
        roommates = user_model.get_users_by_group(current_user.group_id)
        other_members = [r for r in roommates if r['id'] != current_user.id]
        return render_template('reminder/send.html', roommates=other_members)
    except Exception as e:
        flash(f"無法載入成員列表：{e}", "danger")
        return redirect(url_for('dashboard.index'))

@reminder_bp.route('/reminders/send', methods=['POST'])
@login_required
@group_required
def send_reminder():
    receiver_id_str = request.form.get('receiver_id', '').strip()
    category = request.form.get('category', '').strip()
    message = request.form.get('message', '').strip()

    roommates = user_model.get_users_by_group(current_user.group_id)
    other_members = [r for r in roommates if r['id'] != current_user.id]

    if not receiver_id_str or not category or not message:
        flash("所有欄位皆為必填！", "danger")
        return render_template('reminder/send.html', roommates=other_members)

    try:
        receiver_id = int(receiver_id_str)
        if receiver_id == current_user.id:
            flash("您不能發送提醒給自己！", "danger")
            return render_template('reminder/send.html', roommates=other_members)

        # 驗證接收者是否確實同屬該群組
        receiver = user_model.get_by_id(receiver_id)
        if not receiver or receiver['group_id'] != current_user.group_id:
            flash("接收者無效或不屬於此群組！", "danger")
            return render_template('reminder/send.html', roommates=other_members)

        # 冷卻機制檢查（1小時內不可重複發送給同一人）
        recent = reminder_model.get_recent_reminders(current_user.id, receiver_id, limit_hours=1)
        if recent:
            flash("發送失敗：您在 1 小時內已對此室友發送過匿名提醒，請稍候再試！", "warning")
            return render_template('reminder/send.html', roommates=other_members)

        # 建立匿名提醒記錄
        reminder_model.create({
            'group_id': current_user.group_id,
            'sender_id': current_user.id,
            'receiver_id': receiver_id,
            'category': category,
            'message': message
        })

        # 建立被提醒者的站內通知 (完全隱去 sender_id，以系統提示名義發送)
        cat_display = CATEGORY_NAMES.get(category, '生活')
        noti_model.create({
            'user_id': receiver_id,
            'group_id': current_user.group_id,
            'type': 'reminder',
            'title': f'收到一則匿名的【{cat_display}】溫和提醒',
            'message': f'提醒內容：{message}',
            'is_read': 0
        })

        flash("匿名提醒已成功發送！讓系統為您做黑臉，保持宿舍和諧。", "success")
        return redirect(url_for('reminder.send_form'))
    except Exception as e:
        flash(f"發送提醒失敗：{e}", "danger")
        return render_template('reminder/send.html', roommates=other_members)

@reminder_bp.route('/reminders/inbox', methods=['GET'])
@login_required
@group_required
def inbox():
    try:
        reminders = reminder_model.get_by_receiver(current_user.id)
        # 轉換分類顯示文字
        reminders_display = []
        for r in reminders:
            reminders_display.append({
                'id': r['id'],
                'category_display': CATEGORY_NAMES.get(r['category'], r['category']),
                'message': r['message'],
                'created_at': r['created_at']
            })
        return render_template('reminder/inbox.html', reminders=reminders_display)
    except Exception as e:
        flash(f"無法載入提醒收件匣：{e}", "danger")
        return render_template('reminder/inbox.html', reminders=[])

@reminder_bp.route('/reminders/stats', methods=['GET'])
@login_required
@group_required
def stats():
    db_group = group_model.get_by_id(current_user.group_id)
    if not db_group:
        abort(404)

    # 權限檢查：只有管理員（或群組建立者）能查閱提醒統計
    is_admin = (current_user.role == 'admin') or (db_group['created_by'] == current_user.id)
    if not is_admin:
        abort(403)

    try:
        raw_stats = reminder_model.get_stats_by_group(current_user.group_id)
        
        # 轉換分類文字為表格或圖表所需格式
        stats_display = []
        for s in raw_stats:
            stats_display.append({
                'category_display': CATEGORY_NAMES.get(s['category'], s['category']),
                'count': s['count']
            })
            
        return render_template('reminder/stats.html', stats=stats_display)
    except Exception as e:
        flash(f"載入統計摘要失敗：{e}", "danger")
        return render_template('reminder/stats.html', stats=[])
