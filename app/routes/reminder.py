from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.utils.auth_helpers import login_required

reminder_bp = Blueprint('reminder', __name__, url_prefix='/reminder')

@reminder_bp.route('/send', methods=['GET', 'POST'])
@login_required
def reminder_send():
    """發送匿名提醒"""
    if request.method == 'POST':
        pass
    return render_template('reminder/send.html')

@reminder_bp.route('/inbox', methods=['GET'])
@login_required
def reminder_inbox():
    """收到的提醒"""
    return render_template('reminder/inbox.html')

@reminder_bp.route('/stats', methods=['GET'])
@login_required
def reminder_stats():
    """統計摘要 (管理者用)"""
    return render_template('reminder/stats.html')
