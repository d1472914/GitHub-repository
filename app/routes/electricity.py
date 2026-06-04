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

    total_amount_str = request.form.get('total_amount', '').strip()
    total_kwh_str = request.form.get('total_kwh', '').strip()
    period_start = request.form.get('period_start', '').strip()
    period_end = request.form.get('period_end', '').strip()

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
            'total_amount': total_amount,
            'total_kwh': total_kwh,
            'period_start': period_start,
            'period_end': period_end,
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
        
        # ✅ 修正處：將 sqlite3.Row 轉為 dict
        members_map = {m['id']: dict(m) for m in members}
        
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
                'personal_amount': s['personal_amount'],
                'shared_amount': s['shared_amount'],
                'total_amount': s['total_amount'],
                'is_paid': s['is_paid']
            })

        return render_template(
            'electricity/detail.html',
            bill=bill,
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
            'start_reading': start_reading,
            'end_reading': end_reading,
            'personal_kwh': personal_kwh
        })

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