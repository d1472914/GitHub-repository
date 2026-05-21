from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.utils.auth_helpers import login_required

group_bp = Blueprint('group', __name__, url_prefix='/group')

@group_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_group():
    """建立群組"""
    if request.method == 'POST':
        pass
    return render_template('group/create.html')

@group_bp.route('/join', methods=['GET', 'POST'])
@login_required
def join_group():
    """加入群組"""
    if request.method == 'POST':
        pass
    return render_template('group/join.html')

@group_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """群組設定"""
    if request.method == 'POST':
        pass
    return render_template('group/settings.html')
