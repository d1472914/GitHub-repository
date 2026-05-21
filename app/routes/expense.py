"""
共同開支帳本路由 — 記帳列表、新增開支、餘額總覽、結算
Blueprint prefix: /expense
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from app.routes.auth import login_required
from app.models import Expense, ExpenseSplit, User

expense_bp = Blueprint('expense', __name__, url_prefix='/expenses')

@expense_bp.route('', methods=['GET'])
@login_required
def list_page():
    """帳本列表
    - 輸出：expense/list.html
    """
    group_id = g.user['group_id']
    if not group_id:
        flash("請先加入或建立群組！", "warning")
        return redirect(url_for('group.create_page'))

    try:
        # 取得該群組的所有開支記錄
        expenses = Expense.get_by_group_id(group_id)
        
        # 取得所有成員對照字典，方便顯示暱稱
        members = {m['id']: m for m in User.get_by_group_id(group_id)}
        
        # 取得每個開支的分攤明細
        expense_details = []
        for exp in expenses:
            splits = ExpenseSplit.get_by_expense_id(exp['id'])
            split_details = []
            for sp in splits:
                user_nickname = members.get(sp['user_id'], {}).get('nickname', '未知室友')
                split_details.append({
                    'nickname': user_nickname,
                    'amount': sp['amount'],
                    'is_settled': sp['is_settled']
                })
            
            payer = members.get(exp['paid_by'], {}).get('nickname', '未知室友')
            expense_details.append({
                'id': exp['id'],
                'title': exp['title'],
                'amount': exp['amount'],
                'category': exp['category'],
                'payer': payer,
                'created_at': exp['created_at'],
                'splits': split_details
            })

        return render_template('expense/list.html', expenses=expense_details)
    except Exception as e:
        print(f"Error loading expenses: {e}")
        flash("無法載入開支記錄。", "error")
        return redirect(url_for('dashboard.index'))

@expense_bp.route('/new', methods=['GET'])
@login_required
def new_page():
    """顯示新增記帳表單頁面
    - 輸出：expense/form.html
    """
    group_id = g.user['group_id']
    if not group_id:
        flash("請先加入或建立群組！", "warning")
        return redirect(url_for('group.create_page'))

    try:
        # 取得群組內所有成員，供選擇分攤對象
        members = User.get_by_group_id(group_id)
        return render_template('expense/form.html', members=members)
    except Exception as e:
        print(f"Error loading new expense form: {e}")
        flash("載入記帳表單失敗。", "error")
        return redirect(url_for('expense.list_page'))

@expense_bp.route('', methods=['POST'])
@login_required
def create():
    """新增記帳處理
    - 輸入：title, amount, category, split_users[]
    - 處理：Expense.create() → 計算每人分攤金額 → ExpenseSplit.create()
    - 輸出：重導向 /expenses
    """
    group_id = g.user['group_id']
    if not group_id:
        flash("操作無效，您尚未加入群組！", "error")
        return redirect(url_for('dashboard.index'))

    title = request.form.get('title', '').strip()
    amount_str = request.form.get('amount', '').strip()
    category = request.form.get('category', '').strip()
    split_user_ids = request.form.getlist('split_users[]')

    # 1. 基本輸入驗證
    if not title or not amount_str or not category:
        flash("所有欄位均為必填項目！", "error")
        return redirect(url_for('expense.new_page'))

    try:
        amount = float(amount_str)
        if amount <= 0:
            flash("金額必須為正數！", "error")
            return redirect(url_for('expense.new_page'))
    except ValueError:
        flash("請輸入有效的金額數值！", "error")
        return redirect(url_for('expense.new_page'))

    if not split_user_ids:
        flash("請至少選擇一位分攤的室友！", "error")
        return redirect(url_for('expense.new_page'))

    try:
        # 2. 建立開支主表記錄
        expense_id = Expense.create({
            'group_id': group_id,
            'title': title,
            'amount': amount,
            'category': category,
            'paid_by': g.user['id']
        })

        if not expense_id:
            flash("建立開支記錄失敗，請稍後再試。", "error")
            return redirect(url_for('expense.new_page'))

        # 3. 計算並建立分攤明細
        # 包含付款人自己如果他也在分攤名單裡
        num_splits = len(split_user_ids)
        split_amount = round(amount / num_splits, 2)

        for u_id in split_user_ids:
            # 轉換為整數 ID
            user_id = int(u_id)
            ExpenseSplit.create({
                'expense_id': expense_id,
                'user_id': user_id,
                'amount': split_amount,
                'is_settled': 0
            })

        flash("記帳成功，已成功分攤！", "success")
        return redirect(url_for('expense.list_page'))

    except Exception as e:
        print(f"Error creating expense: {e}")
        flash("記帳過程發生伺服器錯誤。", "error")
        return redirect(url_for('expense.new_page'))

@expense_bp.route('/balance', methods=['GET'])
@login_required
def balance_page():
    """餘額總覽
    - 輸出：expense/balance.html
    """
    group_id = g.user['group_id']
    if not group_id:
        flash("請先加入或建立群組！", "warning")
        return redirect(url_for('group.create_page'))

    try:
        members = User.get_by_group_id(group_id)
        current_user_id = g.user['id']
        
        # 兩兩計算未結清餘額
        # 格式：[ { 'user_id': 2, 'nickname': '小明', 'balance': 50.0 } ]
        # balance > 0 代表 current_user 應收小明（小明欠 current_user）
        # balance < 0 代表 current_user 應付小明（current_user 欠小明）
        balances = []
        
        # 取得所有未結清的分攤記錄
        # 1. 取得 current_user 應付他人的分攤 (即 U1 欠別人的)
        unsettled_payables = ExpenseSplit.get_unsettled_by_user(current_user_id)
        
        # 2. 取得他人應付 current_user 的分攤
        # 這需要找出所有 current_user 付款的 expenses 裡，其他人的未結清 splits
        import sqlite3
        conn = sqlite3.connect(Expense.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        sql_receivables = """
            SELECT es.*, e.title, e.amount as total_amount, e.paid_by, e.created_at
            FROM expense_splits es
            JOIN expenses e ON es.expense_id = e.id
            WHERE e.paid_by = ? AND es.user_id != ? AND es.is_settled = 0
        """
        unsettled_receivables = conn.execute(sql_receivables, (current_user_id, current_user_id)).fetchall()
        conn.close()

        # 計算對每個成員的淨額
        members_map = {m['id']: m for m in members if m['id'] != current_user_id}
        net_balances = {m_id: 0.0 for m_id in members_map}

        # 扣減：我欠別人的金額
        for pay in unsettled_payables:
            payer_id = pay['paid_by']
            if payer_id in net_balances:
                net_balances[payer_id] -= pay['amount']

        # 增加：別人欠我的金額
        for rec in unsettled_receivables:
            debtor_id = rec['user_id']
            if debtor_id in net_balances:
                net_balances[debtor_id] += rec['amount']

        # 轉換為前端顯示格式
        for m_id, bal in net_balances.items():
            balances.append({
                'user_id': m_id,
                'nickname': members_map[m_id]['nickname'],
                'balance': round(bal, 2)
            })

        return render_template('expense/balance.html', balances=balances)
        
    except Exception as e:
        print(f"Error calculating balances: {e}")
        flash("無法計算餘額總覽。", "error")
        return redirect(url_for('expense.list_page'))

@expense_bp.route('/settle', methods=['POST'])
@login_required
def settle():
    """結算處理 (只接受 POST)
    - 輸入：settle_with_user_id (結算對象 ID)
    - 處理：標記雙方未結清 splits 為已結清
    - 輸出：重導向 /expenses/balance
    """
    settle_with_user_id_str = request.form.get('settle_with_user_id')
    if not settle_with_user_id_str:
        flash("請指定結算對象！", "error")
        return redirect(url_for('expense.balance_page'))

    try:
        settle_with_user_id = int(settle_with_user_id_str)
        success = ExpenseSplit.mark_settled_between_users(g.user['id'], settle_with_user_id)
        if success:
            flash("結算成功，帳務已結清！", "success")
        else:
            flash("結算失敗，請稍後再試。", "error")
            
        return redirect(url_for('expense.balance_page'))
    except Exception as e:
        print(f"Error settling: {e}")
        flash("結算過程發生伺服器錯誤。", "error")
        return redirect(url_for('expense.balance_page'))
