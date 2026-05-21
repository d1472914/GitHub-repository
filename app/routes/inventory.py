from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.utils.auth_helpers import group_required
from app.models import inventory as inv_model
from app.models import user as user_model
from app.models import expense as expense_model
from app.models import notification as noti_model

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/inventory', methods=['GET'])
@login_required
@group_required
def list_items():
    try:
        items = inv_model.get_by_group(current_user.group_id)
        return render_template('inventory/list.html', items=items)
    except Exception as e:
        flash(f"無法載入物資清單：{e}", "danger")
        return render_template('inventory/list.html', items=[])

@inventory_bp.route('/inventory/new', methods=['GET'])
@login_required
@group_required
def new_item():
    return render_template('inventory/form.html', item=None)

@inventory_bp.route('/inventory', methods=['POST'])
@login_required
@group_required
def create_item():
    name = request.form.get('name', '').strip()
    unit = request.form.get('unit', '').strip()
    quantity_str = request.form.get('quantity', '0').strip()
    min_quantity_str = request.form.get('min_quantity', '0').strip()

    if not name or not unit:
        flash("物資名稱與單位為必填！", "danger")
        return render_template('inventory/form.html', item=None)

    try:
        quantity = int(quantity_str)
        min_quantity = int(min_quantity_str)
        if quantity < 0 or min_quantity < 0:
            raise ValueError
    except ValueError:
        flash("庫存數量與最低庫存量必須是正整數！", "danger")
        return render_template('inventory/form.html', item=None)

    try:
        item_id = inv_model.create({
            'group_id': current_user.group_id,
            'name': name,
            'unit': unit,
            'quantity': quantity,
            'min_quantity': min_quantity,
            'created_by': current_user.id
        })

        # 寫入初始入庫日誌
        if quantity > 0:
            inv_model.create_log({
                'item_id': item_id,
                'user_id': current_user.id,
                'action': 'stock_in',
                'quantity': quantity,
                'note': '初始入庫'
            })

        flash("物資品項建立成功！", "success")
        return redirect(url_for('inventory.list_items'))
    except Exception as e:
        flash(f"建立物資品項失敗：{e}", "danger")
        return render_template('inventory/form.html', item=None)

@inventory_bp.route('/inventory/<int:id>', methods=['GET'])
@login_required
@group_required
def detail_item(id):
    item = inv_model.get_by_id(id)
    if not item or item['group_id'] != current_user.group_id:
        abort(404)

    try:
        logs = inv_model.get_logs_by_item(id)
        roommates = user_model.get_users_by_group(current_user.group_id)
        user_map = {r['id']: r['nickname'] for r in roommates}
        
        log_displays = []
        for lg in logs:
            log_displays.append({
                'id': lg['id'],
                'nickname': user_map.get(lg['user_id'], '未知'),
                'action': lg['action'],
                'quantity': lg['quantity'],
                'note': lg['note'],
                'created_at': lg['created_at']
            })
            
        return render_template('inventory/detail.html', item=item, logs=log_displays)
    except Exception as e:
        flash(f"無法載入物資詳情：{e}", "danger")
        return redirect(url_for('inventory.list_items'))

@inventory_bp.route('/inventory/<int:id>/edit', methods=['GET'])
@login_required
@group_required
def edit_item(id):
    item = inv_model.get_by_id(id)
    if not item or item['group_id'] != current_user.group_id:
        abort(404)
    return render_template('inventory/form.html', item=item)

@inventory_bp.route('/inventory/<int:id>/update', methods=['POST'])
@login_required
@group_required
def update_item(id):
    item = inv_model.get_by_id(id)
    if not item or item['group_id'] != current_user.group_id:
        abort(404)

    name = request.form.get('name', '').strip()
    unit = request.form.get('unit', '').strip()
    min_quantity_str = request.form.get('min_quantity', '0').strip()

    if not name or not unit:
        flash("物資名稱與單位為必填！", "danger")
        return render_template('inventory/form.html', item=item)

    try:
        min_quantity = int(min_quantity_str)
        if min_quantity < 0:
            raise ValueError
    except ValueError:
        flash("最低庫存量必須是正整數！", "danger")
        return render_template('inventory/form.html', item=item)

    try:
        inv_model.update(id, {
            'name': name,
            'unit': unit,
            'min_quantity': min_quantity
        })
        flash("物資品項修改成功！", "success")
        return redirect(url_for('inventory.detail_item', id=id))
    except Exception as e:
        flash(f"修改失敗，資料庫錯誤：{e}", "danger")
        return render_template('inventory/form.html', item=item)

@inventory_bp.route('/inventory/<int:id>/stock-in', methods=['POST'])
@login_required
@group_required
def stock_in(id):
    item = inv_model.get_by_id(id)
    if not item or item['group_id'] != current_user.group_id:
        abort(404)

    qty_str = request.form.get('quantity', '').strip()
    note = request.form.get('note', '').strip()
    sync_expense = request.form.get('sync_expense') == '1'
    amount_str = request.form.get('amount', '0').strip()

    if not qty_str:
        flash("請輸入入庫數量！", "danger")
        return redirect(url_for('inventory.detail_item', id=id))

    try:
        qty = int(qty_str)
        if qty <= 0:
            raise ValueError
    except ValueError:
        flash("入庫數量必須大於 0！", "danger")
        return redirect(url_for('inventory.detail_item', id=id))

    amount = 0.0
    if sync_expense:
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash("若同步至帳本，請輸入有效的購買金額！", "danger")
            return redirect(url_for('inventory.detail_item', id=id))

    try:
        # 更新庫存
        new_qty = item['quantity'] + qty
        inv_model.update(id, {'quantity': new_qty})

        # 新增操作日誌
        inv_model.create_log({
            'item_id': id,
            'user_id': current_user.id,
            'action': 'stock_in',
            'quantity': qty,
            'note': note or '入庫登記'
        })

        # 同步記帳
        if sync_expense:
            roommates = user_model.get_users_by_group(current_user.group_id)
            expense_id = expense_model.create({
                'group_id': current_user.group_id,
                'title': f"購買物資：{item['name']} x{qty} {item['unit']}",
                'amount': amount,
                'category': '日用品',
                'paid_by': current_user.id
            })
            
            # 均分給所有室友
            split_amount = amount / len(roommates)
            for r in roommates:
                expense_model.create_split({
                    'expense_id': expense_id,
                    'user_id': r['id'],
                    'amount': split_amount,
                    'is_settled': 0
                })

        flash("入庫登記成功！" + ("已同步建立共同開支帳目。" if sync_expense else ""), "success")
        return redirect(url_for('inventory.detail_item', id=id))
    except Exception as e:
        flash(f"入庫失敗，資料庫錯誤：{e}", "danger")
        return redirect(url_for('inventory.detail_item', id=id))

@inventory_bp.route('/inventory/<int:id>/stock-out', methods=['POST'])
@login_required
@group_required
def stock_out(id):
    item = inv_model.get_by_id(id)
    if not item or item['group_id'] != current_user.group_id:
        abort(404)

    qty_str = request.form.get('quantity', '').strip()
    note = request.form.get('note', '').strip()

    if not qty_str:
        flash("請輸入消耗數量！", "danger")
        return redirect(url_for('inventory.detail_item', id=id))

    try:
        qty = int(qty_str)
        if qty <= 0:
            raise ValueError
        if qty > item['quantity']:
            raise ValueError("庫存不足！")
    except ValueError as e:
        flash(f"消耗數量無效：{str(e) or '必須是大於 0 的正整數'}", "danger")
        return redirect(url_for('inventory.detail_item', id=id))

    try:
        # 更新庫存
        new_qty = item['quantity'] - qty
        inv_model.update(id, {'quantity': new_qty})

        # 新增操作日誌
        inv_model.create_log({
            'item_id': id,
            'user_id': current_user.id,
            'action': 'stock_out',
            'quantity': qty,
            'note': note or '消耗登記'
        })

        # 低庫存警報
        if new_qty <= item['min_quantity']:
            roommates = user_model.get_users_by_group(current_user.group_id)
            for r in roommates:
                noti_model.create({
                    'user_id': r['id'],
                    'group_id': current_user.group_id,
                    'type': 'inventory',
                    'title': f'物資庫存不足警告：{item["name"]}',
                    'message': f'物資「{item["name"]}」目前庫存僅剩 {new_qty} {item["unit"]}，已低於設定的最低庫存 {item["min_quantity"]} {item["unit"]}，請儘速採購！',
                    'is_read': 0
                })

        flash("消耗登記成功！" + ("警告：庫存已低於最低門檻，已通知所有成員！" if new_qty <= item['min_quantity'] else ""), "success")
        return redirect(url_for('inventory.detail_item', id=id))
    except Exception as e:
        flash(f"消耗登記失敗，資料庫錯誤：{e}", "danger")
        return redirect(url_for('inventory.detail_item', id=id))
