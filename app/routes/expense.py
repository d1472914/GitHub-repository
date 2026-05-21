<<<<<<< HEAD
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
=======
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.utils.auth_helpers import group_required
from app.utils import calc_helpers
from app.models import expense as expense_model
from app.models import user as user_model

expense_bp = Blueprint('expense', __name__)

@expense_bp.route('/expenses', methods=['GET'])
@login_required
@group_required
def list_expenses():
    try:
        expenses = expense_model.get_by_group(current_user.group_id)
        roommates = user_model.get_users_by_group(current_user.group_id)
        user_map = {r['id']: r['nickname'] for r in roommates}
        
        # 針對每筆支出取得分攤名單與狀態
        expense_details = []
        for e in expenses:
            splits = expense_model.get_splits_by_expense(e['id'])
            split_details = []
            for s in splits:
                split_details.append({
                    'nickname': user_map.get(s['user_id'], '未知使用者'),
                    'amount': s['amount'],
                    'is_settled': s['is_settled']
                })
            expense_details.append({
                'id': e['id'],
                'title': e['title'],
                'amount': e['amount'],
                'category': e['category'] or '未分類',
                'paid_by_name': user_map.get(e['paid_by'], '未知使用者'),
                'paid_by_id': e['paid_by'],
                'created_at': e['created_at'],
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
                'splits': split_details
            })

        return render_template('expense/list.html', expenses=expense_details)
    except Exception as e:
<<<<<<< HEAD
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
=======
        flash(f"無法載入開支列表：{e}", "danger")
        return render_template('expense/list.html', expenses=[])

@expense_bp.route('/expenses/new', methods=['GET'])
@login_required
@group_required
def new_expense():
    try:
        roommates = user_model.get_users_by_group(current_user.group_id)
        return render_template('expense/form.html', members=roommates)
    except Exception as e:
        flash(f"無法載入室友名單：{e}", "danger")
        return redirect(url_for('expense.list_expenses'))

@expense_bp.route('/expenses', methods=['POST'])
@login_required
@group_required
def create_expense():
    title = request.form.get('title', '').strip()
    amount_str = request.form.get('amount', '').strip()
    category = request.form.get('category', '').strip()
    split_users = request.form.getlist('split_users[]')

    roommates = user_model.get_users_by_group(current_user.group_id)

    # 驗證
    if not title:
        flash("請輸入開支項目名稱！", "danger")
        return render_template('expense/form.html', members=roommates)
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b

    try:
        amount = float(amount_str)
        if amount <= 0:
<<<<<<< HEAD
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
=======
            raise ValueError
    except ValueError:
        flash("請輸入大於 0 的有效金額！", "danger")
        return render_template('expense/form.html', members=roommates)

    if not split_users:
        flash("請選擇至少一位分攤對象！", "danger")
        return render_template('expense/form.html', members=roommates)

    try:
        # 新增開支
        expense_id = expense_model.create({
            'group_id': current_user.group_id,
            'title': title,
            'amount': amount,
            'category': category or None,
            'paid_by': current_user.id
        })

        # 計算每人分攤金額
        split_amount = amount / len(split_users)

        # 寫入分攤
        for uid_str in split_users:
            uid = int(uid_str)
            expense_model.create_split({
                'expense_id': expense_id,
                'user_id': uid,
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
                'amount': split_amount,
                'is_settled': 0
            })

<<<<<<< HEAD
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
=======
        flash("記帳成功！", "success")
        return redirect(url_for('expense.list_expenses'))
    except Exception as e:
        flash(f"記帳失敗，資料庫錯誤：{e}", "danger")
        return render_template('expense/form.html', members=roommates)

@expense_bp.route('/expenses/balance', methods=['GET'])
@login_required
@group_required
def balance():
    try:
        roommates = user_model.get_users_by_group(current_user.group_id)
        expenses = expense_model.get_by_group(current_user.group_id)
        splits = expense_model.get_splits_by_group(current_user.group_id)
        
        # 計算餘額
        balances = calc_helpers.calculate_expense_balances(roommates, expenses, splits)
        
        # 對應室友暱稱，為了前端方便渲染
        balances_display = []
        for r in roommates:
            bal = balances.get(r['id'], 0.0)
            balances_display.append({
                'user_id': r['id'],
                'nickname': r['nickname'],
                'balance': bal
            })
            
        return render_template('expense/balance.html', balances=balances_display, current_user_id=current_user.id)
    except Exception as e:
        flash(f"無法載入餘額：{e}", "danger")
        return render_template('expense/balance.html', balances=[], current_user_id=current_user.id)

@expense_bp.route('/expenses/settle', methods=['POST'])
@login_required
@group_required
def settle():
    settle_with_user_id_str = request.form.get('settle_with_user_id')
    if not settle_with_user_id_str:
        flash("請選擇要結清的室友！", "danger")
        return redirect(url_for('expense.balance'))

    try:
        settle_with_user_id = int(settle_with_user_id_str)
        expenses = expense_model.get_by_group(current_user.group_id)
        splits = expense_model.get_splits_by_group(current_user.group_id)
        
        expense_paid_by = {e['id']: e['paid_by'] for e in expenses}
        
        settled_count = 0
        for s in splits:
            if s['is_settled']:
                continue
                
            expense_id = s['expense_id']
            payer_id = expense_paid_by.get(expense_id)
            if not payer_id:
                continue
                
            debtor_id = s['user_id']
            
            # 條件一：我付的，對方分攤的
            # 條件二：對方付的，我分攤的
            is_match1 = (payer_id == current_user.id and debtor_id == settle_with_user_id)
            is_match2 = (payer_id == settle_with_user_id and debtor_id == current_user.id)
            
            if is_match1 or is_match2:
                expense_model.update_split(s['id'], {'is_settled': 1})
                settled_count += 1
                
        flash(f"結算完成！已結清 {settled_count} 筆分攤款項。", "success")
        return redirect(url_for('expense.balance'))
    except Exception as e:
        flash(f"結清失敗，資料庫錯誤：{e}", "danger")
        return redirect(url_for('expense.balance'))
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
