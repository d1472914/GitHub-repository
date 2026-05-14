"""
共同開支帳本路由 — 記帳、分攤、餘額、結算
Blueprint prefix: /expenses
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash

expense_bp = Blueprint('expense', __name__, url_prefix='/expenses')


@expense_bp.route('', methods=['GET'])
def list_expenses():
    """帳本列表
    - 處理：Expense.get_by_group(current_user.group_id)
    - 輸出：expense/list.html
    """
    pass


@expense_bp.route('/new', methods=['GET'])
def new_page():
    """新增記帳頁面
    - 輸出：expense/form.html（含群組成員列表供勾選分攤對象）
    """
    pass


@expense_bp.route('', methods=['POST'])
def create():
    """新增記帳處理
    - 輸入：title, amount, category, split_users[]
    - 處理：Expense.create() → 計算分攤 → ExpenseSplit.create() for each user
    - 輸出：重導向 /expenses
    """
    pass


@expense_bp.route('/balance', methods=['GET'])
def balance():
    """餘額總覽
    - 處理：計算群組內每人的應收/應付淨額
    - 輸出：expense/balance.html
    """
    pass


@expense_bp.route('/settle', methods=['POST'])
def settle():
    """結算處理
    - 輸入：settle_with_user_id
    - 處理：找出雙方未結清分攤 → 標記 is_settled=True
    - 輸出：重導向 /expenses/balance
    """
    pass
