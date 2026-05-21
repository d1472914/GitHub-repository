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
                'splits': split_details
            })

        return render_template('expense/list.html', expenses=expense_details)
    except Exception as e:
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

    try:
        amount = float(amount_str)
        if amount <= 0:
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
                'amount': split_amount,
                'is_settled': 0
            })

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
