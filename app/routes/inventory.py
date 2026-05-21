from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.utils.auth_helpers import group_required
from app.models.inventory_item import InventoryItem
from app.models.inventory_log import InventoryLog
from app.models.expense import Expense
from app.models.expense_split import ExpenseSplit
from app.models.user import User
from app.models.notification import Notification

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/')
@login_required
@group_required
def list_items():
    """物資庫存列表"""
    items = InventoryItem.get_by_group(current_user.group_id)
    return render_template('inventory/list.html', items=items)

@inventory_bp.route('/new', methods=['GET', 'POST'])
@login_required
@group_required
def create_item():
    """新增物資品項"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        unit = request.form.get('unit', '').strip()
        quantity_str = request.form.get('quantity', '0').strip()
        min_quantity_str = request.form.get('min_quantity', '0').strip()
        
        if not name or not unit or not quantity_str or not min_quantity_str:
            flash('所有欄位皆為必填！', 'warning')
            return render_template('inventory/form.html', name=name, unit=unit, quantity=quantity_str, min_quantity=min_quantity_str, action_type='new')
            
        try:
            quantity = int(quantity_str)
            min_quantity = int(min_quantity_str)
            if quantity < 0 or min_quantity < 0:
                raise ValueError()
        except ValueError:
            flash('數量與最低庫存量必須為非負整數！', 'warning')
            return render_template('inventory/form.html', name=name, unit=unit, quantity=quantity_str, min_quantity=min_quantity_str, action_type='new')
            
        item_data = {
            'group_id': current_user.group_id,
            'name': name,
            'unit': unit,
            'quantity': quantity,
            'min_quantity': min_quantity,
            'created_by': current_user.id
        }
        
        new_item = InventoryItem.create(item_data)
        if new_item:
            # 建立初始入庫日誌
            if quantity > 0:
                InventoryLog.create({
                    'item_id': new_item.id,
                    'user_id': current_user.id,
                    'action': 'in',
                    'quantity': quantity,
                    'note': '初始建立入庫'
                })
            flash(f'成功新增物資「{name}」！', 'success')
            return redirect(url_for('inventory.list_items'))
        else:
            flash('新增物資失敗，請重試。', 'danger')
            
    return render_template('inventory/form.html', action_type='new')

@inventory_bp.route('/<int:item_id>')
@login_required
@group_required
def detail(item_id):
    """物資詳情與異動日誌"""
    item = InventoryItem.get_by_id(item_id)
    if not item or item.group_id != current_user.group_id:
        flash('找不到該物資品項！', 'danger')
        return redirect(url_for('inventory.list_items'))
        
    logs = InventoryLog.get_by_item(item_id)
    return render_template('inventory/detail.html', item=item, logs=logs)

@inventory_bp.route('/<int:item_id>/stock-in', methods=['POST'])
@login_required
@group_required
def stock_in(item_id):
    """物資入庫 (增加庫存)"""
    item = InventoryItem.get_by_id(item_id)
    if not item or item.group_id != current_user.group_id:
        flash('找不到該物資品項！', 'danger')
        return redirect(url_for('inventory.list_items'))
        
    qty_str = request.form.get('quantity', '').strip()
    note = request.form.get('note', '').strip()
    sync_expense = request.form.get('sync_expense') == '1'
    expense_amount_str = request.form.get('expense_amount', '').strip()
    
    if not qty_str:
        flash('請輸入入庫數量！', 'warning')
        return redirect(url_for('inventory.detail', item_id=item_id))
        
    try:
        qty = int(qty_str)
        if qty <= 0:
            raise ValueError()
    except ValueError:
        flash('入庫數量必須是正整數！', 'warning')
        return redirect(url_for('inventory.detail', item_id=item_id))
        
    if item.stock_in(qty):
        # 建立入庫日誌
        InventoryLog.create({
            'item_id': item_id,
            'user_id': current_user.id,
            'action': 'in',
            'quantity': qty,
            'note': note or '一般入庫'
        })
        
        # 同步記帳整合 (將物資採購費用記在開支帳本，並均攤給全體室友)
        if sync_expense and expense_amount_str:
            try:
                expense_amount = float(expense_amount_str)
                if expense_amount > 0:
                    # 建立 Expense
                    new_exp = Expense.create({
                        'group_id': current_user.group_id,
                        'title': f'物資採購：{item.name} x {qty} {item.unit}',
                        'amount': expense_amount,
                        'category': '雜物',
                        'paid_by': current_user.id
                    })
                    
                    if new_exp:
                        members = User.get_by_group(current_user.group_id)
                        split_amount = round(expense_amount / len(members), 2)
                        for m in members:
                            is_settled = 1 if (m.id == current_user.id and len(members) == 1) else 0
                            ExpenseSplit.create({
                                'expense_id': new_exp.id,
                                'user_id': m.id,
                                'amount': split_amount,
                                'is_settled': is_settled
                            })
                            
                            if m.id != current_user.id:
                                Notification.create({
                                    'user_id': m.id,
                                    'group_id': current_user.group_id,
                                    'type': 'expense',
                                    'title': '物資採購記帳通知',
                                    'message': f'室友 {current_user.nickname} 採購了公用物資 {item.name} 並同步記帳 ${expense_amount}，您需分攤 ${split_amount}。'
                                })
                        flash('入庫登記成功，且採購金額已同步至開支帳本！', 'success')
            except ValueError:
                flash('同步記帳失敗：請輸入正確的金額。但入庫已成功登記。', 'warning')
        else:
            flash(f'物資「{item.name}」已成功入庫 {qty} {item.unit}！', 'success')
    else:
        flash('入庫登記失敗，請重試。', 'danger')
        
    return redirect(url_for('inventory.detail', item_id=item_id))

@inventory_bp.route('/<int:item_id>/stock-out', methods=['POST'])
@login_required
@group_required
def stock_out(item_id):
    """物資出庫 (消耗庫存)"""
    item = InventoryItem.get_by_id(item_id)
    if not item or item.group_id != current_user.group_id:
        flash('找不到該物資品項！', 'danger')
        return redirect(url_for('inventory.list_items'))
        
    qty_str = request.form.get('quantity', '').strip()
    note = request.form.get('note', '').strip()
    
    if not qty_str:
        flash('請輸入消耗數量！', 'warning')
        return redirect(url_for('inventory.detail', item_id=item_id))
        
    try:
        qty = int(qty_str)
        if qty <= 0:
            raise ValueError()
        if qty > item.quantity:
            flash(f'庫存不足！目前庫存僅剩 {item.quantity} {item.unit}。', 'warning')
            return redirect(url_for('inventory.detail', item_id=item_id))
    except ValueError:
        flash('消耗數量必須是正整數！', 'warning')
        return redirect(url_for('inventory.detail', item_id=item_id))
        
    if item.stock_out(qty):
        # 建立出庫日誌
        InventoryLog.create({
            'item_id': item_id,
            'user_id': current_user.id,
            'action': 'out',
            'quantity': qty,
            'note': note or '一般消耗'
        })
        
        # 檢查低庫存提醒
        if item.is_low_stock:
            # 發送低庫存通知給全體室友
            members = User.get_by_group(current_user.group_id)
            for m in members:
                Notification.create({
                    'user_id': m.id,
                    'group_id': current_user.group_id,
                    'type': 'inventory',
                    'title': '公用物資低庫存提醒 🚨',
                    'message': f'警告：物資「{item.name}」目前庫存已降至 {item.quantity} {item.unit}，低於最低設定量 {item.min_quantity} {item.unit}，請室友抽空補貨。'
                })
            flash(f'已消耗 {qty} {item.unit}。目前庫存已低於警戒線，已通知室友補貨！', 'warning')
        else:
            flash(f'已消耗 {qty} {item.unit}。目前剩餘庫存：{item.quantity} {item.unit}。', 'success')
    else:
        flash('出庫登記失敗，請重試。', 'danger')
        
    return redirect(url_for('inventory.detail', item_id=item_id))

@inventory_bp.route('/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
@group_required
def edit_item(item_id):
    """編輯物資品項屬性"""
    item = InventoryItem.get_by_id(item_id)
    if not item or item.group_id != current_user.group_id:
        flash('找不到該物資品項！', 'danger')
        return redirect(url_for('inventory.list_items'))
        
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        unit = request.form.get('unit', '').strip()
        min_quantity_str = request.form.get('min_quantity', '').strip()
        
        if not name or not unit or not min_quantity_str:
            flash('所有欄位皆為必填！', 'warning')
            return render_template('inventory/form.html', item=item, action_type='edit')
            
        try:
            min_quantity = int(min_quantity_str)
            if min_quantity < 0:
                raise ValueError()
        except ValueError:
            flash('最低庫存量必須是非負整數！', 'warning')
            return render_template('inventory/form.html', item=item, action_type='edit')
            
        InventoryItem.update(item_id, {
            'name': name,
            'unit': unit,
            'min_quantity': min_quantity
        })
        
        flash('物資資訊已更新！', 'success')
        return redirect(url_for('inventory.detail', item_id=item_id))
        
    return render_template('inventory/form.html', item=item, action_type='edit')

@inventory_bp.route('/<int:item_id>/delete', methods=['POST'])
@login_required
@group_required
def delete_item(item_id):
    """刪除物資"""
    item = InventoryItem.get_by_id(item_id)
    if not item or item.group_id != current_user.group_id:
        flash('找不到該物資品項！', 'danger')
        return redirect(url_for('inventory.list_items'))
        
    if item.created_by != current_user.id and current_user.role != 'admin':
        flash('只有物資建立者或群組管理員才能刪除此項目！', 'danger')
        return redirect(url_for('inventory.detail', item_id=item_id))
        
    if InventoryItem.delete(item_id):
        flash('物資品項已成功刪除！', 'info')
    else:
        flash('刪除物資失敗，請重試。', 'danger')
        
    return redirect(url_for('inventory.list_items'))
