"""
友善黑臉路由 — 發送匿名提醒、收件匣、管理統計
Blueprint prefix: /reminders
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, g, abort
from app.routes.auth import login_required
from app.models import Reminder, Notification, User

reminder_bp = Blueprint('reminder', __name__, url_prefix='/reminders')

@reminder_bp.route('/send', methods=['GET'])
@login_required
def send_page():
    """顯示發送匿名提醒表單頁面
    - 輸出：reminder/send.html
    """
    group_id = g.user['group_id']
    if not group_id:
        flash("請先加入或建立群組！", "warning")
        return redirect(url_for('group.create_page'))

    try:
        # 取得群組內「其他」成員，供選擇提醒對象
        members = [m for m in User.get_by_group_id(group_id) if m['id'] != g.user['id']]
        return render_template('reminder/send.html', members=members)
    except Exception as e:
        print(f"Error loading reminder form: {e}")
        flash("載入發送表單失敗。", "error")
        return redirect(url_for('dashboard.index'))

@reminder_bp.route('/send', methods=['POST'])
@login_required
def send():
    """發送匿名提醒處理
    - 輸入：receiver_id, category, message
    - 處理：Reminder.check_cooldown() → Reminder.create() → Notification.create()
    - 輸出：成功 → 重導向 /reminders/send；冷卻中 → 回到表單
    """
    group_id = g.user['group_id']
    if not group_id:
        flash("操作無效，您尚未加入群組！", "error")
        return redirect(url_for('dashboard.index'))

    receiver_id_str = request.form.get('receiver_id', '').strip()
    category = request.form.get('category', '').strip()
    message = request.form.get('message', '').strip()

    if not receiver_id_str or not category or not message:
        flash("所有欄位均為必填！", "error")
        return redirect(url_for('reminder.send_page'))

    try:
        receiver_id = int(receiver_id_str)
        
        # 1. 驗證不可發送給自己
        if receiver_id == g.user['id']:
            flash("您不可以發送提醒給自己！", "error")
            return redirect(url_for('reminder.send_page'))

        # 2. 驗證接收者是否在同一個群組
        receiver = User.get_by_id(receiver_id)
        if not receiver or receiver['group_id'] != group_id:
            flash("該接收者不存在或不屬於您的宿舍群組！", "error")
            return redirect(url_for('reminder.send_page'))

        # 3. 檢查發言冷卻時間 (1 小時)
        recent_reminder = Reminder.check_cooldown(g.user['id'], receiver_id, hours=1)
        if recent_reminder:
            flash("冷卻中！您在一小時內已對該室友發送過提醒，請稍後再試。", "warning")
            return redirect(url_for('reminder.send_page'))

        # 4. 建立匿名提醒記錄
        reminder_id = Reminder.create({
            'group_id': group_id,
            'sender_id': g.user['id'],
            'receiver_id': receiver_id,
            'category': category,
            'message': message
        })

        if reminder_id:
            # 5. 發送系統站內通知 (⚠️ 標題和內文不含 sender_id，以維持匿名性)
            Notification.create({
                'user_id': receiver_id,
                'group_id': group_id,
                'type': 'reminder',
                'title': f"🤫 收到一則【{category}】的匿名生活提醒",
                'message': message
            })
            
            flash("匿名提醒已成功發送！", "success")
        else:
            flash("發送失敗，請稍後再試。", "error")

        return redirect(url_for('reminder.send_page'))

    except Exception as e:
        print(f"Error sending reminder: {e}")
        flash("發送提醒時發生伺服器錯誤。", "error")
        return redirect(url_for('reminder.send_page'))

@reminder_bp.route('/inbox', methods=['GET'])
@login_required
def inbox():
    """提醒收件匣
    - 輸出：reminder/inbox.html
    """
    try:
        # 收到的匿名提醒列表 (後端不回傳 sender_id 確保安全)
        reminders = Reminder.get_inbox_by_user(g.user['id'])
        return render_template('reminder/inbox.html', reminders=reminders)
    except Exception as e:
        print(f"Error loading inbox: {e}")
        flash("載入收件匣失敗。", "error")
        return redirect(url_for('dashboard.index'))

@reminder_bp.route('/stats', methods=['GET'])
@login_required
def stats():
    """統計摘要
    - 處理：限管理員 (admin) 存取，統計類別數量
    - 輸出：reminder/stats.html
    - 錯誤：非管理者 → 403 Forbidden
    """
    if g.user['role'] != 'admin':
        abort(403)  # 403 拒絕存取

    group_id = g.user['group_id']
    if not group_id:
        flash("請先加入或建立群組！", "warning")
        return redirect(url_for('group.create_page'))

    try:
        stats_data = Reminder.get_stats_by_group(group_id)
        
        # 整理成字典或列表傳給前端
        categories = []
        counts = []
        for row in stats_data:
            categories.append(row['category'])
            counts.append(row['count'])

        return render_template(
            'reminder/stats.html',
            stats=stats_data,
            categories=categories,
            counts=counts
        )
    except Exception as e:
        print(f"Error loading reminder stats: {e}")
        flash("載入統計數據失敗。", "error")
        return redirect(url_for('dashboard.index'))
