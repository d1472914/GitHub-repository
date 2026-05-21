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
    total_amount_str = request.form.get('total_amount', '').strip()
    total_kwh_str = request.form.get('total_kwh', '').strip()
    period_start = request.form.get('period_start', '').strip()
    period_end = request.form.get('period_end', '').strip()

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
            'total_amount': total_amount,
            'total_kwh': total_kwh,
            'period_start': period_start,
            'period_end': period_end,
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
                'personal_amount': s['personal_amount'],
                'shared_amount': s['shared_amount'],
                'total_amount': s['total_amount'],
                'is_paid': s['is_paid']
            })

        return render_template(
            'electricity/detail.html',
            bill=bill,
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
            'start_reading': start_reading,
            'end_reading': end_reading,
            'personal_kwh': personal_kwh
        })

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
