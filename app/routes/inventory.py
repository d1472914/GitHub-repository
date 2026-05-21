<<<<<<< HEAD
"""
共同物資庫存路由 — 物資清單、新增物資、物資詳情與出入庫歷史、編輯物資、入出庫登記
Blueprint prefix: /inventory
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from app.routes.auth import login_required
from app.models import InventoryItem, InventoryLog, Notification, Expense, ExpenseSplit, User

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@inventory_bp.route('', methods=['GET'])
@login_required
def list_page():
    """物資清單
    - 輸出：inventory/list.html
    """
    group_id = g.user['group_id']
    if not group_id:
        flash("請先加入或建立群組！", "warning")
        return redirect(url_for('group.create_page'))

    try:
        items = InventoryItem.get_by_group_id(group_id)
        return render_template('inventory/list.html', items=items)
    except Exception as e:
        print(f"Error loading inventory items: {e}")
        flash("無法載入物資清單。", "error")
        return redirect(url_for('dashboard.index'))

@inventory_bp.route('/new', methods=['GET'])
@login_required
def new_page():
    """新增物資頁面
    - 輸出：inventory/form.html
    """
    if not g.user['group_id']:
        flash("請先加入或建立群組！", "warning")
        return redirect(url_for('group.create_page'))
    return render_template('inventory/form.html', item=None)

@inventory_bp.route('', methods=['POST'])
@login_required
def create():
    """新增物資處理
    - 輸入：name, unit, quantity, min_quantity
    - 處理：InventoryItem.create()
    - 輸出：重導向 /inventory
    """
    group_id = g.user['group_id']
    if not group_id:
        flash("操作無效，您尚未加入群組！", "error")
        return redirect(url_for('dashboard.index'))

    name = request.form.get('name', '').strip()
    unit = request.form.get('unit', '個').strip()
=======
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
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
    quantity_str = request.form.get('quantity', '0').strip()
    min_quantity_str = request.form.get('min_quantity', '0').strip()

    if not name or not unit:
<<<<<<< HEAD
        flash("物資名稱與單位為必填項目！", "error")
=======
        flash("物資名稱與單位為必填！", "danger")
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
        return render_template('inventory/form.html', item=None)

    try:
        quantity = int(quantity_str)
        min_quantity = int(min_quantity_str)
        if quantity < 0 or min_quantity < 0:
<<<<<<< HEAD
            flash("數量與最低警戒庫存量不可為負數！", "error")
            return render_template('inventory/form.html', item=None)
    except ValueError:
        flash("請輸入有效的整數數量值！", "error")
        return render_template('inventory/form.html', item=None)

    try:
        item_id = InventoryItem.create({
            'group_id': group_id,
=======
            raise ValueError
    except ValueError:
        flash("庫存數量與最低庫存量必須是正整數！", "danger")
        return render_template('inventory/form.html', item=None)

    try:
        item_id = inv_model.create({
            'group_id': current_user.group_id,
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
            'name': name,
            'unit': unit,
            'quantity': quantity,
            'min_quantity': min_quantity,
<<<<<<< HEAD
            'created_by': g.user['id']
        })

        if item_id:
            # 建立初始入庫的 Log 記錄
            if quantity > 0:
                InventoryLog.create({
                    'item_id': item_id,
                    'user_id': g.user['id'],
                    'action': 'stock_in',
                    'quantity': quantity,
                    'note': '初始商品入庫'
                })
            
            flash(f"物資「{name}」新增成功！", "success")
            return redirect(url_for('inventory.list_page'))
        else:
            flash("新增物資失敗，請稍後再試。", "error")
            return render_template('inventory/form.html', item=None)

    except Exception as e:
        print(f"Error creating inventory item: {e}")
        flash("新增物資時發生伺服器錯誤。", "error")
        return redirect(url_for('inventory.list_page'))

@inventory_bp.route('/<int:item_id>', methods=['GET'])
@login_required
def detail_page(item_id):
    """物資詳情與入出庫歷史
    - 輸出：inventory/detail.html
    """
    try:
        item = InventoryItem.get_by_id(item_id)
        if not item or item['group_id'] != g.user['group_id']:
            flash("找不到該物資，或您無權限存取！", "error")
            return redirect(url_for('inventory.list_page'))

        # 取得歷史操作記錄
        logs = InventoryLog.get_by_item(item_id)
        members = {m['id']: m for m in User.get_by_group_id(g.user['group_id'])}
        
        log_details = []
        for l in logs:
            operator_name = members.get(l['user_id'], {}).get('nickname', '未知室友')
            log_details.append({
                'id': l['id'],
                'operator': operator_name,
                'action': '入庫' if l['action'] == 'stock_in' else '出庫',
                'quantity': l['quantity'],
                'note': l['note'],
                'created_at': l['created_at']
            })

        return render_template('inventory/detail.html', item=item, logs=log_details)
    except Exception as e:
        print(f"Error loading inventory details: {e}")
        flash("載入物資詳情失敗。", "error")
        return redirect(url_for('inventory.list_page'))

@inventory_bp.route('/<int:item_id>/edit', methods=['GET'])
@login_required
def edit_page(item_id):
    """顯示編輯物資頁面
    - 輸出：inventory/form.html
    """
    try:
        item = InventoryItem.get_by_id(item_id)
        if not item or item['group_id'] != g.user['group_id']:
            flash("找不到該物資，或您無編輯權限！", "error")
            return redirect(url_for('inventory.list_page'))
            
        return render_template('inventory/form.html', item=item)
    except Exception as e:
        print(f"Error loading inventory edit form: {e}")
        flash("載入編輯頁面失敗。", "error")
        return redirect(url_for('inventory.list_page'))

@inventory_bp.route('/<int:item_id>/update', methods=['POST'])
@login_required
def update(item_id):
    """更新物資 (只接受 POST)
    - 輸入：name, unit, min_quantity
    - 處理：InventoryItem.update()
    - 輸出：重導向 /inventory/<id>
    """
    try:
        item = InventoryItem.get_by_id(item_id)
        if not item or item['group_id'] != g.user['group_id']:
            flash("物資不存在，或您無權限修改！", "error")
            return redirect(url_for('inventory.list_page'))

        name = request.form.get('name', '').strip()
        unit = request.form.get('unit', '個').strip()
        min_quantity_str = request.form.get('min_quantity', '0').strip()

        if not name or not unit:
            flash("物資名稱與單位為必填項目！", "error")
            return render_template('inventory/form.html', item=item)

        try:
            min_quantity = int(min_quantity_str)
            if min_quantity < 0:
                flash("最低警戒庫存量不可為負數！", "error")
                return render_template('inventory/form.html', item=item)
        except ValueError:
            flash("請輸入有效的整數警戒值！", "error")
            return render_template('inventory/form.html', item=item)

        success = InventoryItem.update(item_id, {
=======
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
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
            'name': name,
            'unit': unit,
            'min_quantity': min_quantity
        })
<<<<<<< HEAD

        if success:
            flash("物資資訊更新成功！", "success")
        else:
            flash("物資無變更或更新失敗。", "info")
            
        return redirect(url_for('inventory.detail_page', item_id=item_id))

    except Exception as e:
        print(f"Error updating inventory item: {e}")
        flash("更新物資發生伺服器錯誤。", "error")
        return redirect(url_for('inventory.list_page'))

@inventory_bp.route('/<int:item_id>/stock-in', methods=['POST'])
@login_required
def stock_in(item_id):
    """入庫登記 (只接受 POST)
    - 輸入：quantity, note, sync_expense (1 or 0), expense_amount
    - 處理：InventoryItem.adjust_stock() + InventoryLog.create() + (選) Expense.create()
    - 輸出：重導向 /inventory/<id>
    """
    try:
        item = InventoryItem.get_by_id(item_id)
        if not item or item['group_id'] != g.user['group_id']:
            flash("找不到該物資！", "error")
            return redirect(url_for('inventory.list_page'))

        quantity_str = request.form.get('quantity', '').strip()
        note = request.form.get('note', '').strip()
        sync_expense = request.form.get('sync_expense') == '1'
        expense_amount_str = request.form.get('expense_amount', '').strip()

        if not quantity_str:
            flash("入庫數量為必填項目！", "error")
            return redirect(url_for('inventory.detail_page', item_id=item_id))

        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                flash("入庫數量必須大於 0！", "error")
                return redirect(url_for('inventory.detail_page', item_id=item_id))
        except ValueError:
            flash("請輸入有效的正整數入庫數量！", "error")
            return redirect(url_for('inventory.detail_page', item_id=item_id))

        # 1. 調整庫存
        adjust_success = InventoryItem.adjust_stock(item_id, quantity)
        if not adjust_success:
            flash("庫存調整失敗。", "error")
            return redirect(url_for('inventory.detail_page', item_id=item_id))

        # 2. 建立 Log 記錄
        InventoryLog.create({
            'item_id': item_id,
            'user_id': g.user['id'],
            'action': 'stock_in',
            'quantity': quantity,
            'note': note or '一般入庫'
        })

        # 3. 如果勾選同步記帳，則同時在共同開支中記錄 (全體室友平均分攤)
        if sync_expense:
            try:
                expense_amount = float(expense_amount_str) if expense_amount_str else (quantity * 10.0) # 預設一單位 $10 元
                if expense_amount > 0:
                    group_id = g.user['group_id']
                    expense_id = Expense.create({
                        'group_id': group_id,
                        'title': f"購置物資：{item['name']} (x{quantity})",
                        'amount': expense_amount,
                        'category': "日常物資",
                        'paid_by': g.user['id']
                    })
                    
                    if expense_id:
                        members = User.get_by_group_id(group_id)
                        split_amount = round(expense_amount / len(members), 2)
                        for m in members:
                            ExpenseSplit.create({
                                'expense_id': expense_id,
                                'user_id': m['id'],
                                'amount': split_amount,
                                'is_settled': 0
                            })
                        flash(f"入庫成功！並同步新增共同記帳：${expense_amount}", "success")
                    else:
                        flash("入庫成功，但同步共同開支記錄失敗。", "warning")
                else:
                    flash("入庫成功！由於記帳金額非正數，故未進行同步記帳。", "warning")
            except ValueError:
                flash("入庫成功！由於記帳金額格式錯誤，故未進行同步記帳。", "warning")
        else:
            flash("物資入庫成功！", "success")

        return redirect(url_for('inventory.detail_page', item_id=item_id))

    except Exception as e:
        print(f"Error stocking in: {e}")
        flash("入庫登記發生伺服器錯誤。", "error")
        return redirect(url_for('inventory.list_page'))

@inventory_bp.route('/<int:item_id>/stock-out', methods=['POST'])
@login_required
def stock_out(item_id):
    """出庫登記 (只接受 POST)
    - 輸入：quantity, note
    - 處理：InventoryItem.adjust_stock() + InventoryLog.create() + 低於警示庫存發送通知
    - 輸出：重導向 /inventory/<id>
    """
    try:
        item = InventoryItem.get_by_id(item_id)
        if not item or item['group_id'] != g.user['group_id']:
            flash("找不到該物資！", "error")
            return redirect(url_for('inventory.list_page'))

        quantity_str = request.form.get('quantity', '').strip()
        note = request.form.get('note', '').strip()

        if not quantity_str:
            flash("出庫數量為必填項目！", "error")
            return redirect(url_for('inventory.detail_page', item_id=item_id))

        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                flash("出庫數量必須大於 0！", "error")
                return redirect(url_for('inventory.detail_page', item_id=item_id))
            if item['quantity'] < quantity:
                flash(f"出庫失敗！庫存量不足（現有 {item['quantity']}，擬出庫 {quantity}）！", "error")
                return redirect(url_for('inventory.detail_page', item_id=item_id))
        except ValueError:
            flash("請輸入有效的正整數出庫數量！", "error")
            return redirect(url_for('inventory.detail_page', item_id=item_id))

        # 1. 調整庫存 (出庫為負數)
        adjust_success = InventoryItem.adjust_stock(item_id, -quantity)
        if not adjust_success:
            flash("庫存出庫調整失敗。", "error")
            return redirect(url_for('inventory.detail_page', item_id=item_id))

        # 2. 建立 Log 記錄
        InventoryLog.create({
            'item_id': item_id,
            'user_id': g.user['id'],
            'action': 'stock_out',
            'quantity': quantity,
            'note': note or '一般領用出庫'
        })

        flash("物資出庫領用登記成功！", "success")

        # 3. 取得最新庫存並檢查是否低於警戒值 (min_quantity)
        updated_item = InventoryItem.get_by_id(item_id)
        if updated_item['quantity'] <= updated_item['min_quantity']:
            # 對群組內「所有」成員發送低庫存系統通知
            members = User.get_by_group_id(g.user['group_id'])
            for m in members:
                Notification.create({
                    'user_id': m['id'],
                    'group_id': g.user['group_id'],
                    'type': 'inventory',
                    'title': f"⚠️ 物資存量不足警告：{updated_item['name']}",
                    'message': f"公用物資【{updated_item['name']}】的目前存量為 {updated_item['quantity']} {updated_item['unit']}，低於設定的最低警示值 {updated_item['min_quantity']} {updated_item['unit']}。請室友儘速安排時間採購補充！"
                })
            flash("警告：該物資庫存已降至最低警示值以下，已自動通知全體室友！", "warning")

        return redirect(url_for('inventory.detail_page', item_id=item_id))

    except Exception as e:
        print(f"Error stocking out: {e}")
        flash("出庫登記發生伺服器錯誤。", "error")
        return redirect(url_for('inventory.list_page'))
=======
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
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
