from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.utils.auth_helpers import group_required
from app.models.reminder import Reminder
from app.models.user import User
from app.models.notification import Notification

reminder_bp = Blueprint('reminder', __name__)

# 預設的友善黑臉提醒語錄庫
PRESET_TEMPLATES = {
    'noise': [
        "哈囉～現在的音量好像有點大喔！可以稍微降低一點點嗎？感謝啦！🙌",
        "嗨嗨，不知道是不是錯覺，聲音好像傳到我這了。麻煩留意一下音量唷～🎵",
        "親愛的室友，目前音量微超標，為了美好的居住品質，麻煩小聲一點點唷！✨"
    ],
    'hygiene': [
        "哈囉！公共區域好像有一些垃圾/雜物喔，有空的話再麻煩幫忙清理一下，感恩！🧹",
        "嗨～水槽裡的碗盤好像堆了一陣子囉，動動手洗一洗吧，感謝配合！🍽️",
        "室友們～公共區域（浴室/客廳）輪到值日生打掃囉，再抽空整理一下，謝啦！🧽"
    ],
    'other': [
        "溫馨提醒：出門或睡前要記得關好冷氣與門窗，注意省電與安全唷！🔌",
        "嗨嗨，有空記得繳交最近的各項均攤費用（如房租、水電費）喔，感謝！💵",
        "親愛的室友，有空可以幫忙補一下低庫存的共同物資嗎？辛苦啦！🛒"
    ]
}

@reminder_bp.route('/inbox')
@login_required
@group_required
def inbox():
    """匿名提醒收件匣"""
    reminders = Reminder.get_by_receiver(current_user.id)
    return render_template('reminder/inbox.html', reminders=reminders)

@reminder_bp.route('/send', methods=['GET', 'POST'])
@login_required
@group_required
def send_reminder():
    """發送匿名提醒"""
    members = User.get_by_group(current_user.group_id)
    # 過濾出其他室友
    roommates = [m for m in members if m.id != current_user.id]
    
    if request.method == 'POST':
        receiver_id = request.form.get('receiver', type=int)
        category = request.form.get('category', '').strip()
        message_type = request.form.get('message_type', 'preset') # 'preset' 或 'custom'
        
        # 取得訊息內容
        if message_type == 'preset':
            message = request.form.get('preset_message', '').strip()
        else:
            message = request.form.get('custom_message', '').strip()
            
        # 驗證
        if not receiver_id or not category or not message:
            flash('請填寫指派對象、類別與提醒內容！', 'warning')
            return render_template('reminder/send.html', roommates=roommates, templates=PRESET_TEMPLATES, receiver=receiver_id, category=category, message_type=message_type)
            
        # 檢查冷卻時間 (1小時限一次)
        if Reminder.check_cooldown(current_user.id, receiver_id):
            flash('您在一小時內已發送過提醒給該室友，請稍候再試。', 'warning')
            return render_template('reminder/send.html', roommates=roommates, templates=PRESET_TEMPLATES, receiver=receiver_id, category=category, message_type=message_type)
            
        # 建立提醒
        reminder_data = {
            'group_id': current_user.group_id,
            'sender_id': current_user.id,
            'receiver_id': receiver_id,
            'category': category,
            'message': message
        }
        
        new_rem = Reminder.create(reminder_data)
        if new_rem:
            # 發送系統通知給接收者
            # 由於要保證匿名，在通知中直接以「系統匿名提醒」發送，不出現 sender 的名稱
            category_zh = {'noise': '噪音管理', 'hygiene': '衛生清潔', 'other': '其他事項'}.get(category, '生活事項')
            Notification.create({
                'user_id': receiver_id,
                'group_id': current_user.group_id,
                'type': 'reminder',
                'title': f'您收到了一則【{category_zh}】匿名提醒',
                'message': f'系統提醒：有室友提醒您：「{message}」'
            })
            
            flash('匿名提醒已成功發送！讓系統為您當黑臉。', 'success')
            return redirect(url_for('reminder.inbox'))
        else:
            flash('發送提醒失敗，請重試。', 'danger')
            
    return render_template('reminder/send.html', roommates=roommates, templates=PRESET_TEMPLATES)

@reminder_bp.route('/stats')
@login_required
@group_required
def stats():
    """群組提醒數據統計"""
    stats_map = Reminder.get_stats_by_group(current_user.group_id)
    # 格式化為前端圖表或列表數據
    categories_zh = {
        'noise': '噪音管理',
        'hygiene': '衛生清潔',
        'other': '其他約定'
    }
    
    formatted_stats = []
    total_count = 0
    for key, name in categories_zh.items():
        count = stats_map.get(key, 0)
        formatted_stats.append({
            'key': key,
            'name': name,
            'count': count
        })
        total_count += count
        
    return render_template('reminder/stats.html', stats=formatted_stats, total=total_count)
