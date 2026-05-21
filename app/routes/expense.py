from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.utils.auth_helpers import group_required
from app.models.expense import Expense
from app.models.expense_split import ExpenseSplit
from app.models.user import User
from app.models.notification import Notification
from app.models import get_db_connection

expense_bp = Blueprint('expense', __name__)

def calculate_debts(group_id):
    """計算群組內各成員之間的債務關係"""
    members = User.get_by_group(group_id)
    # 建立雙向餘額矩陣 balances[payer_id][debtor_id]
    balances = {m.id: {other.id: 0.0 for other in members if other.id != m.id} for m in members}
    
    conn = get_db_connection()
    # 查詢未結清的分攤，且付款人不等於分攤人
    query = """
        SELECT e.paid_by, s.user_id, s.amount 
        FROM expense_splits s
        JOIN expenses e ON s.expense_id = e.id
        WHERE e.group_id = ? AND s.is_settled = 0 AND s.user_id != e.paid_by
    """
    rows = conn.execute(query, (group_id,)).fetchall()
    conn.close()
    
    for row in rows:
        payer = row['paid_by']
        debtor = row['user_id']
        amount = row['amount']
        if payer in balances and debtor in balances[payer]:
            balances[payer][debtor] += amount
            
    debts = []
    processed = set()
    for m1 in members:
        for m2 in members:
            if m1.id == m2.id or (m1.id, m2.id) in processed or (m2.id, m1.id) in processed:
                continue
            processed.add((m1.id, m2.id))
            
            owes_m1 = balances[m1.id][m2.id] # m2 欠 m1
            owes_m2 = balances[m2.id][m1.id] # m1 欠 m2
            
            if owes_m1 > owes_m2:
                net = owes_m1 - owes_m2
                debts.append({
                    'from_user': m2,
                    'to_user': m1,
                    'amount': round(net, 2)
                })
            elif owes_m2 > owes_m1:
                net = owes_m2 - owes_m1
                debts.append({
                    'from_user': m1,
                    'to_user': m2,
                    'amount': round(net, 2)
                })
    return debts

@expense_bp.route('/')
@login_required
@group_required
def list_expenses():
    """帳本首頁"""
    expenses = Expense.get_by_group(current_user.group_id)
    members = User.get_by_group(current_user.group_id)
    members_dict = {m.id: m for m in members}
    
    # 獲取每個開支的詳情與分攤情況
    expenses_data = []
    for exp in expenses:
        splits = ExpenseSplit.get_by_expense(exp.id)
        # 過濾出不是付款人自己的分攤 (展示給使用者看誰分攤了)
        split_details = []
        for sp in splits:
            member = members_dict.get(sp.user_id)
            split_details.append({
                'nickname': member.nickname if member else '未知',
                'amount': sp.amount,
                'is_settled': sp.is_settled
            })
            
        payer = members_dict.get(exp.paid_by)
        expenses_data.append({
            'info': exp,
            'payer_name': payer.nickname if payer else '未知',
            'splits': split_details
        })
        
    # 計算結算債務
    debts = calculate_debts(current_user.group_id)
    
    return render_template('expense/list.html', expenses=expenses_data, debts=debts)

@expense_bp.route('/new', methods=['GET', 'POST'])
@login_required
@group_required
def create_expense():
    """記帳"""
    members = User.get_by_group(current_user.group_id)
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        amount_str = request.form.get('amount', '').strip()
        category = request.form.get('category', '').strip()
        paid_by_id = request.form.get('paid_by', type=int)
        split_user_ids = request.form.getlist('split_users', type=int)
        
        # 驗證
        if not title or not amount_str or not paid_by_id or not split_user_ids:
            flash('請填寫必填欄位並選擇至少一位分攤人！', 'warning')
            return render_template('expense/form.html', members=members, title=title, amount=amount_str, category=category)
            
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            flash('請輸入有效的正數金額！', 'warning')
            return render_template('expense/form.html', members=members, title=title, amount=amount_str, category=category)
            
        # 建立開支
        expense_data = {
            'group_id': current_user.group_id,
            'title': title,
            'amount': amount,
            'category': category or '其他',
            'paid_by': paid_by_id
        }
        
        new_expense = Expense.create(expense_data)
        if new_expense:
            # 計算均分金額
            split_amount = round(amount / len(split_user_ids), 2)
            
            # 寫入分攤
            for uid in split_user_ids:
                # 如果分攤人就是付款人，且只有一個人分攤，則為已結清 (防呆)
                # 否則預設為未結清 (0)
                is_settled = 1 if (uid == paid_by_id and len(split_user_ids) == 1) else 0
                # 如果分攤人是付款人本人，則在帳本結算中不計入債務，但寫入 DB 方便查詢
                ExpenseSplit.create({
                    'expense_id': new_expense.id,
                    'user_id': uid,
                    'amount': split_amount,
                    'is_settled': is_settled
                })
                
                # 發送通知給被分攤者 (排除付款人自己)
                if uid != paid_by_id:
                    payer = next((m for m in members if m.id == paid_by_id), current_user)
                    Notification.create({
                        'user_id': uid,
                        'group_id': current_user.group_id,
                        'type': 'expense',
                        'title': '新增開支分攤',
                        'message': f'室友 {payer.nickname} 記了一筆「{title}」（${amount}），您需分攤 ${split_amount}。'
                    })
                    
            flash('記帳成功！已為室友建立分攤帳務。', 'success')
            return redirect(url_for('expense.list_expenses'))
        else:
            flash('記帳失敗，請重試。', 'danger')
            
    return render_template('expense/form.html', members=members)

@expense_bp.route('/settle', methods=['POST'])
@login_required
@group_required
def settle_expense():
    """結清雙方債務"""
    from_user_id = request.form.get('from_user_id', type=int)
    to_user_id = request.form.get('to_user_id', type=int)
    
    if not from_user_id or not to_user_id:
        flash('無效的結清請求！', 'danger')
        return redirect(url_for('expense.list_expenses'))
        
    # 進行結算：將 to_user_id 幫 from_user_id 付的，以及 from_user_id 幫 to_user_id 付的皆標記為已結清
    # 也就是說，把 user1=to_user_id, user2=from_user_id 的所有 split.is_settled 設為 1
    success = ExpenseSplit.settle_splits(to_user_id, from_user_id)
    if success:
        from_user = User.get_by_id(from_user_id)
        to_user = User.get_by_id(to_user_id)
        
        # 發送通知
        Notification.create({
            'user_id': from_user_id,
            'group_id': current_user.group_id,
            'type': 'expense',
            'title': '帳務已結清',
            'message': f'您與室友 {to_user.nickname} 之間的未結清帳務已由 {current_user.nickname} 標記為已結清。'
        })
        Notification.create({
            'user_id': to_user_id,
            'group_id': current_user.group_id,
            'type': 'expense',
            'title': '帳務已結清',
            'message': f'您與室友 {from_user.nickname} 之間的未結清帳務已由 {current_user.nickname} 標記為已結清。'
        })
        
        flash(f'已結清 {from_user.nickname} 與 {to_user.nickname} 之間的所有開支帳務！', 'success')
    else:
        flash('結清帳務失敗，請稍後再試。', 'danger')
        
    return redirect(url_for('expense.list_expenses'))

@expense_bp.route('/<int:expense_id>/delete', methods=['POST'])
@login_required
@group_required
def delete_expense(expense_id):
    """刪除開支"""
    expense = Expense.get_by_id(expense_id)
    if not expense or expense.group_id != current_user.group_id:
        flash('找不到該筆開支！', 'danger')
        return redirect(url_for('expense.list_expenses'))
        
    if expense.paid_by != current_user.id and current_user.role != 'admin':
        flash('只有付款人或群組管理員才能刪除此帳目！', 'danger')
        return redirect(url_for('expense.list_expenses'))
        
    if Expense.delete(expense_id):
        flash('開支帳目已成功刪除！', 'info')
    else:
        flash('刪除失敗，請重試。', 'danger')
        
    return redirect(url_for('expense.list_expenses'))
