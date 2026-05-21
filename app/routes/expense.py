from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.utils.auth_helpers import login_required

expense_bp = Blueprint('expense', __name__, url_prefix='/expense')

@expense_bp.route('/', methods=['GET'])
@login_required
def expense_list():
    """帳本列表"""
    return render_template('expense/list.html')

@expense_bp.route('/balance', methods=['GET'])
@login_required
def expense_balance():
    """餘額總覽"""
    return render_template('expense/balance.html')

@expense_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    """新增消費記錄"""
    if request.method == 'POST':
        pass
    return render_template('expense/form.html')
