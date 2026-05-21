"""
友善黑臉路由 — 匿名提醒發送、收件匣、統計
Blueprint prefix: /reminders
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash

reminder_bp = Blueprint('reminder', __name__, url_prefix='/reminders')


@reminder_bp.route('/send', methods=['GET'])
def send_page():
    """發送提醒頁面
    - 處理：取得群組成員列表（排除自己）與提醒範本
    - 輸出：reminder/send.html
    """
    pass


@reminder_bp.route('/send', methods=['POST'])
def send():
    """發送提醒處理
    - 輸入：receiver_id, category, message
    - 處理：Reminder.check_cooldown() → Reminder.create() → Notification.create()（不含 sender）
    - 輸出：成功 → 重導向 /reminders/send；冷卻中 → 回到表單
    - 錯誤：冷卻未結束、不能發給自己
    """
    pass


@reminder_bp.route('/inbox', methods=['GET'])
def inbox():
    """提醒收件匣
    - 處理：Reminder.get_received_by_user(current_user.id)（不含 sender 資訊）
    - 輸出：reminder/inbox.html
    """
    pass


@reminder_bp.route('/stats', methods=['GET'])
def stats():
    """統計摘要（管理者專用）
    - 處理：Reminder.get_stats_by_group() 取得類別統計
    - 輸出：reminder/stats.html
    - 錯誤：非管理者 → 403
    """
    pass
