<<<<<<< HEAD
"""
智慧電費路由 — 帳單列表、新增帳單、帳單詳情、電表登錄與分攤計算
Blueprint prefix: /electricity
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from app.routes.auth import login_required
from app.models import ElectricityBill, MeterReading, ElectricitySplit, User

electricity_bp = Blueprint('electricity', __name__, url_prefix='/electricity')

@electricity_bp.route('', methods=['GET'])
@login_required
def list_page():
    """帳單列表
    - 輸出：electricity/list.html
    """
    group_id = g.user['group_id']
    if not group_id:
        flash("請先加入或建立群組！", "warning")
        return redirect(url_for('group.create_page'))

    try:
        bills = ElectricityBill.get_by_group_id(group_id)
        return render_template('electricity/list.html', bills=bills)
    except Exception as e:
        print(f"Error loading electricity bills: {e}")
        flash("載入電費帳單失敗。", "error")
        return redirect(url_for('dashboard.index'))

@electricity_bp.route('/new', methods=['GET'])
@login_required
def new_page():
    """顯示帳單登錄表單頁面
    - 輸出：electricity/form.html
    """
    if not g.user['group_id']:
        flash("請先加入或建立群組！", "warning")
        return redirect(url_for('group.create_page'))
    return render_template('electricity/form.html')

@electricity_bp.route('', methods=['POST'])
@login_required
def create():
    """新增帳單處理
    - 輸入：total_amount, total_kwh, period_start, period_end
    - 處理：ElectricityBill.create()
    - 輸出：重導向 /electricity
    """
    group_id = g.user['group_id']
    if not group_id:
        flash("操作無效，您尚未加入群組！", "error")
        return redirect(url_for('dashboard.index'))

=======
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.utils.auth_helpers import group_required
from app.utils import calc_helpers
from app.models import electricity as elec_model
from app.models import user as user_model
from app.models import notification as noti_model

electricity_bp = Blueprint('electricity', __name__)

@electricity_bp.route('/electricity', methods=['GET'])
@login_required
@group_required
def list_bills():
    try:
        bills = elec_model.get_by_group(current_user.group_id)
        roommates = user_model.get_users_by_group(current_user.group_id)
        user_map = {r['id']: r['nickname'] for r in roommates}
        
        bill_displays = []
        for b in bills:
            readings = elec_model.get_readings_by_bill(b['id'])
            splits = elec_model.get_splits_by_bill(b['id'])
            
            bill_displays.append({
                'id': b['id'],
                'total_amount': b['total_amount'],
                'total_kwh': b['total_kwh'],
                'period_start': b['period_start'],
                'period_end': b['period_end'],
                'creator_name': user_map.get(b['created_by'], '未知'),
                'readings_count': len(readings),
                'splits_count': len(splits),
                'is_complete': len(splits) > 0
            })
            
        return render_template('electricity/list.html', bills=bill_displays)
    except Exception as e:
        flash(f"無法載入電費帳單列表：{e}", "danger")
        return render_template('electricity/list.html', bills=[])

@electricity_bp.route('/electricity/new', methods=['GET'])
@login_required
@group_required
def new_bill():
    return render_template('electricity/form.html', bill=None)

@electricity_bp.route('/electricity', methods=['POST'])
@login_required
@group_required
def create_bill():
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
    total_amount_str = request.form.get('total_amount', '').strip()
    total_kwh_str = request.form.get('total_kwh', '').strip()
    period_start = request.form.get('period_start', '').strip()
    period_end = request.form.get('period_end', '').strip()

<<<<<<< HEAD
    if not total_amount_str or not total_kwh_str or not period_start or not period_end:
        flash("所有欄位均為必填！", "error")
        return render_template('electricity/form.html')

    try:
        total_amount = float(total_amount_str)
        total_kwh = float(total_kwh_str)
        if total_amount <= 0 or total_kwh <= 0:
            flash("金額與度數必須大於 0！", "error")
            return render_template('electricity/form.html')
    except ValueError:
        flash("請輸入有效的數字金額與度數！", "error")
        return render_template('electricity/form.html')

    try:
        bill_id = ElectricityBill.create({
            'group_id': group_id,
=======
    if not total_amount_str or not period_start or not period_end:
        flash("總金額與計費期間起迄日皆為必填！", "danger")
        return render_template('electricity/form.html', bill=None)

    try:
        total_amount = float(total_amount_str)
        if total_amount <= 0:
            raise ValueError
    except ValueError:
        flash("總金額必須是正數！", "danger")
        return render_template('electricity/form.html', bill=None)

    total_kwh = None
    if total_kwh_str:
        try:
            total_kwh = float(total_kwh_str)
            if total_kwh <= 0:
                raise ValueError
        except ValueError:
            flash("總用電度數若填寫，必須是正數！", "danger")
            return render_template('electricity/form.html', bill=None)

    try:
        bill_id = elec_model.create({
            'group_id': current_user.group_id,
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
            'total_amount': total_amount,
            'total_kwh': total_kwh,
            'period_start': period_start,
            'period_end': period_end,
<<<<<<< HEAD
            'created_by': g.user['id']
        })

        if bill_id:
            flash("電費帳單登錄成功！請通知室友們登錄電表度數以進行分攤計算。", "success")
            return redirect(url_for('electricity.list_page'))
        else:
            flash("帳單建立失敗，請稍後再試。", "error")
            return render_template('electricity/form.html')

    except Exception as e:
        print(f"Error creating electricity bill: {e}")
        flash("建立帳單發生伺服器錯誤。", "error")
        return render_template('electricity/form.html')

@electricity_bp.route('/<int:bill_id>', methods=['GET'])
@login_required
def detail_page(bill_id):
    """帳單詳情與分攤明細
    - 輸出：electricity/detail.html
    """
    try:
        bill = ElectricityBill.get_by_id(bill_id)
        if not bill or bill['group_id'] != g.user['group_id']:
            flash("找不到該電費帳單或您沒有權限存取！", "error")
            return redirect(url_for('electricity.list_page'))

        # 取得已提交的度數記錄與分攤結果
        readings = MeterReading.get_by_bill_id(bill_id)
        splits = ElectricitySplit.get_by_bill_id(bill_id)
        members = User.get_by_group_id(g.user['group_id'])
        
        # 對照字典
        members_map = {m['id']: m for m in members}
        
        # 整理登錄進度與已提交名單
        submitted_user_ids = [r['user_id'] for r in readings]
        has_submitted = g.user['id'] in submitted_user_ids

        # 包裝顯示資料
        reading_details = []
        for r in readings:
            reading_details.append({
                'nickname': members_map.get(r['user_id'], {}).get('nickname', '未知室友'),
                'start_reading': r['start_reading'],
                'end_reading': r['end_reading'],
                'personal_kwh': r['personal_kwh']
            })

        split_details = []
        for s in splits:
            split_details.append({
                'nickname': members_map.get(s['user_id'], {}).get('nickname', '未知室友'),
=======
            'created_by': current_user.id
        })

        # 發通知給所有室友
        roommates = user_model.get_users_by_group(current_user.group_id)
        for r in roommates:
            noti_model.create({
                'user_id': r['id'],
                'group_id': current_user.group_id,
                'type': 'electricity',
                'title': '新電費帳單已登錄',
                'message': f'計費期間 {period_start} 至 {period_end} 的電費帳單已登錄，金額 NT${total_amount}。請儘速登錄您的電表度數！',
                'is_read': 0
            })

        flash("電費帳單登錄成功！已通知所有室友填寫電表度數。", "success")
        return redirect(url_for('electricity.detail_bill', id=bill_id))
    except Exception as e:
        flash(f"登錄帳單失敗，資料庫錯誤：{e}", "danger")
        return render_template('electricity/form.html', bill=None)

@electricity_bp.route('/electricity/<int:id>', methods=['GET'])
@login_required
@group_required
def detail_bill(id):
    bill = elec_model.get_by_id(id)
    if not bill or bill['group_id'] != current_user.group_id:
        abort(404)

    try:
        readings = elec_model.get_readings_by_bill(id)
        splits = elec_model.get_splits_by_bill(id)
        roommates = user_model.get_users_by_group(current_user.group_id)
        user_map = {r['id']: r['nickname'] for r in roommates}
        
        # 檢查當前使用者是否已填寫度數
        user_reading = next((r for r in readings if r['user_id'] == current_user.id), None)
        
        # 組合度數登錄狀態
        readings_status = []
        for r in roommates:
            reading = next((rd for rd in readings if rd['user_id'] == r['id']), None)
            readings_status.append({
                'nickname': r['nickname'],
                'user_id': r['id'],
                'has_submitted': reading is not None,
                'start_reading': reading['start_reading'] if reading else None,
                'end_reading': reading['end_reading'] if reading else None,
                'personal_kwh': reading['personal_kwh'] if reading else None
            })
            
        # 組合分攤明細與繳納狀態
        splits_display = []
        for s in splits:
            splits_display.append({
                'id': s['id'],
                'nickname': user_map.get(s['user_id'], '未知'),
                'user_id': s['user_id'],
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
                'personal_amount': s['personal_amount'],
                'shared_amount': s['shared_amount'],
                'total_amount': s['total_amount'],
                'is_paid': s['is_paid']
            })

        return render_template(
            'electricity/detail.html',
            bill=bill,
<<<<<<< HEAD
            readings=reading_details,
            splits=split_details,
            members=members,
            submitted_user_ids=submitted_user_ids,
            has_submitted=has_submitted
        )
    except Exception as e:
        print(f"Error loading bill detail: {e}")
        flash("載入帳單詳情失敗。", "error")
        return redirect(url_for('electricity.list_page'))

@electricity_bp.route('/<int:bill_id>/meter', methods=['GET'])
@login_required
def meter_page(bill_id):
    """顯示登錄電表度數頁面
    - 輸出：electricity/meter_form.html
    """
    try:
        bill = ElectricityBill.get_by_id(bill_id)
        if not bill or bill['group_id'] != g.user['group_id']:
            flash("找不到該電費帳單或您沒有權限存取！", "error")
            return redirect(url_for('electricity.list_page'))
            
        # 檢查是否已填寫過
        existing = MeterReading.get_by_bill_and_user(bill_id, g.user['id'])
        if existing:
            flash("您已經登錄過這一期的電表度數了！", "info")
            return redirect(url_for('electricity.detail_page', bill_id=bill_id))

        return render_template('electricity/meter_form.html', bill=bill)
    except Exception as e:
        print(f"Error loading meter page: {e}")
        flash("載入電表登錄表單失敗。", "error")
        return redirect(url_for('electricity.list_page'))

@electricity_bp.route('/<int:bill_id>/meter', methods=['POST'])
@login_required
def submit_meter(bill_id):
    """登錄電表處理
    - 輸入：start_reading, end_reading
    - 處理：MeterReading.create() → 檢查全體室友登錄 → 計算並建立 ElectricitySplit
    - 輸出：重導向 /electricity/<id>
    """
    try:
        bill = ElectricityBill.get_by_id(bill_id)
        if not bill or bill['group_id'] != g.user['group_id']:
            flash("找不到該帳單！", "error")
            return redirect(url_for('electricity.list_page'))

        # 1. 檢查是否已填寫過
        existing = MeterReading.get_by_bill_and_user(bill_id, g.user['id'])
        if existing:
            flash("您已經登錄過這一期電表度數了！", "info")
            return redirect(url_for('electricity.detail_page', bill_id=bill_id))

        start_reading_str = request.form.get('start_reading', '').strip()
        end_reading_str = request.form.get('end_reading', '').strip()

        if not start_reading_str or not end_reading_str:
            flash("所有欄位均為必填！", "error")
            return render_template('electricity/meter_form.html', bill=bill)

        try:
            start_reading = float(start_reading_str)
            end_reading = float(end_reading_str)
            if start_reading < 0 or end_reading < 0:
                flash("電表度數不可為負數！", "error")
                return render_template('electricity/meter_form.html', bill=bill)
            if end_reading < start_reading:
                flash("期末度數不可小於期初度數！", "error")
                return render_template('electricity/meter_form.html', bill=bill)
        except ValueError:
            flash("請輸入有效的電表度數數值！", "error")
            return render_template('electricity/meter_form.html', bill=bill)

        # 2. 建立度數登錄記錄
        personal_kwh = end_reading - start_reading
        reading_id = MeterReading.create({
            'bill_id': bill_id,
            'user_id': g.user['id'],
=======
            readings_status=readings_status,
            splits=splits_display,
            user_reading=user_reading,
            roommates_count=len(roommates),
            readings_count=len(readings)
        )
    except Exception as e:
        flash(f"無法載入帳單詳情：{e}", "danger")
        return redirect(url_for('electricity.list_bills'))

@electricity_bp.route('/electricity/<int:id>/meter', methods=['GET'])
@login_required
@group_required
def meter_form(id):
    bill = elec_model.get_by_id(id)
    if not bill or bill['group_id'] != current_user.group_id:
        abort(404)
        
    readings = elec_model.get_readings_by_bill(id)
    # 檢查是否已填寫
    user_reading = next((r for r in readings if r['user_id'] == current_user.id), None)
    if user_reading:
        flash("您已對本期帳單登錄過電表度數！", "warning")
        return redirect(url_for('electricity.detail_bill', id=id))
        
    return render_template('electricity/meter_form.html', bill=bill)

@electricity_bp.route('/electricity/<int:id>/meter', methods=['POST'])
@login_required
@group_required
def create_meter_reading(id):
    bill = elec_model.get_by_id(id)
    if not bill or bill['group_id'] != current_user.group_id:
        abort(404)

    start_str = request.form.get('start_reading', '').strip()
    end_str = request.form.get('end_reading', '').strip()

    if not start_str or not end_str:
        flash("起始與結束度數皆為必填！", "danger")
        return render_template('electricity/meter_form.html', bill=bill)

    try:
        start_reading = float(start_str)
        end_reading = float(end_str)
        if start_reading < 0 or end_reading < 0:
            raise ValueError("度數不能小於 0")
        if end_reading < start_reading:
            raise ValueError("結束度數不能小於起始度數")
    except ValueError as e:
        flash(f"輸入的度數無效：{e}", "danger")
        return render_template('electricity/meter_form.html', bill=bill)

    try:
        personal_kwh = end_reading - start_reading
        elec_model.create_reading({
            'bill_id': id,
            'user_id': current_user.id,
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
            'start_reading': start_reading,
            'end_reading': end_reading,
            'personal_kwh': personal_kwh
        })

<<<<<<< HEAD
        if not reading_id:
            flash("登錄電表失敗，請稍後再試。", "error")
            return render_template('electricity/meter_form.html', bill=bill)

        flash("電表度數登錄成功！", "success")

        # 3. 檢查全體室友是否都已填寫
        members = User.get_by_group_id(g.user['group_id'])
        readings = MeterReading.get_by_bill_id(bill_id)

        if len(readings) >= len(members):
            # 全體填寫完畢，進行電費分攤計算
            total_amount = bill['total_amount']
            total_kwh = bill['total_kwh']
            
            total_personal_kwh = sum(r['personal_kwh'] for r in readings)
            shared_kwh = max(0.0, total_kwh - total_personal_kwh)
            
            unit_price = total_amount / total_kwh if total_kwh > 0 else 0.0

            # 清除原先可能存在的分攤記錄（防呆）
            existing_splits = ElectricitySplit.get_by_bill_id(bill_id)
            for es in existing_splits:
                ElectricitySplit.delete(es['id'])

            for r in readings:
                personal_amount = round(r['personal_kwh'] * unit_price, 2)
                shared_amount = round((shared_kwh * unit_price) / len(members), 2)
                split_total = round(personal_amount + shared_amount, 2)

                ElectricitySplit.create({
                    'bill_id': bill_id,
                    'user_id': r['user_id'],
                    'personal_amount': personal_amount,
                    'shared_amount': shared_amount,
                    'total_amount': split_total,
                    'is_paid': 0
                })

            flash("全體室友已完成電表登錄，智慧分攤帳單已自動計算生成！", "success")

        return redirect(url_for('electricity.detail_page', bill_id=bill_id))

    except Exception as e:
        print(f"Error submitting meter reading: {e}")
        flash("登錄電表時發生伺服器錯誤。", "error")
        return redirect(url_for('electricity.list_page'))
=======
        # 檢查是否所有室友皆已填寫
        roommates = user_model.get_users_by_group(current_user.group_id)
        readings = elec_model.get_readings_by_bill(id)

        if len(readings) >= len(roommates):
            # 自動計算分攤
            splits = calc_helpers.calculate_electricity_splits(
                bill['total_amount'],
                bill['total_kwh'],
                readings,
                roommates
            )

            # 寫入分攤結果並通知室友
            for sp in splits:
                elec_model.create_split({
                    'bill_id': id,
                    'user_id': sp['user_id'],
                    'personal_amount': sp['personal_amount'],
                    'shared_amount': sp['shared_amount'],
                    'total_amount': sp['total_amount'],
                    'is_paid': 0
                })
                
                # 站內通知
                noti_model.create({
                    'user_id': sp['user_id'],
                    'group_id': current_user.group_id,
                    'type': 'electricity',
                    'title': '電費分攤已結算',
                    'message': f'您本期電費應繳 NT${sp["total_amount"]}（個人：NT${sp["personal_amount"]}，公用均攤：NT${sp["shared_amount"]}）。請儘速繳費！',
                    'is_read': 0
                })

            flash("電表度數登錄成功！所有成員皆已登錄，電費分攤計算完成！", "success")
        else:
            flash("電表度數登錄成功！等待其他成員登錄以進行分攤計算。", "success")

        return redirect(url_for('electricity.detail_bill', id=id))
    except Exception as e:
        flash(f"登錄度數失敗，資料庫錯誤：{e}", "danger")
        return render_template('electricity/meter_form.html', bill=bill)

@electricity_bp.route('/electricity/split/<int:split_id>/pay', methods=['POST'])
@login_required
@group_required
def pay_split(split_id):
    try:
        # 標記繳費狀態
        is_paid = request.form.get('is_paid') == '1'
        elec_model.update_split_status(split_id, is_paid)
        flash("繳費狀態更新成功！", "success")
    except Exception as e:
        flash(f"更新繳費狀態失敗：{e}", "danger")
        
    # 重導向回上一頁
    ref = request.referrer or url_for('electricity.list_bills')
    return redirect(ref)
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
