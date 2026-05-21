from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.utils.auth_helpers import group_required
from app.models.electricity_bill import ElectricityBill
from app.models.meter_reading import MeterReading
from app.models.electricity_split import ElectricitySplit
from app.models.user import User
from app.models.notification import Notification

electricity_bp = Blueprint('electricity', __name__)

def calculate_electricity_splits_for_bill(bill_id):
    """計算特定電費帳單的室友分攤費用"""
    bill = ElectricityBill.get_by_id(bill_id)
    if not bill:
        return False
        
    members = User.get_by_group(bill.group_id)
    readings = MeterReading.get_by_bill(bill_id)
    
    # 唯有當所有成員都上傳度數後才進行計算
    if len(readings) < len(members):
        return False
        
    # 清除舊的分攤記錄
    import sqlite3
    from app.models import get_db_connection
    conn = get_db_connection()
    conn.execute("DELETE FROM electricity_splits WHERE bill_id = ?", (bill_id,))
    conn.commit()
    conn.close()
    
    total_amount = bill.total_amount
    total_kwh = bill.total_kwh if bill.total_kwh else 0.0
    
    # 如果總度數 <= 0，直接均分
    if total_kwh <= 0:
        shared_amount = round(total_amount / len(members), 2)
        for m in members:
            ElectricitySplit.create({
                'bill_id': bill_id,
                'user_id': m.id,
                'personal_amount': 0.0,
                'shared_amount': shared_amount,
                'total_amount': shared_amount,
                'is_paid': 0
            })
        return True
        
    kwh_rate = total_amount / total_kwh
    sum_personal_kwh = sum(r.personal_kwh for r in readings)
    public_kwh = max(0.0, total_kwh - sum_personal_kwh)
    shared_kwh_cost_per_person = (public_kwh * kwh_rate) / len(members)
    
    for r in readings:
        personal_amount = round(r.personal_kwh * kwh_rate, 2)
        shared_amount = round(shared_kwh_cost_per_person, 2)
        total_amount_i = personal_amount + shared_amount
        
        ElectricitySplit.create({
            'bill_id': bill_id,
            'user_id': r.user_id,
            'personal_amount': personal_amount,
            'shared_amount': shared_amount,
            'total_amount': total_amount_i,
            'is_paid': 0
        })
        
        # 發送通知給室友
        Notification.create({
            'user_id': r.user_id,
            'group_id': bill.group_id,
            'type': 'electricity',
            'title': '電費帳單已結算完成',
            'message': f'您的電費 (期間 {bill.period_start} ~ {bill.period_end}) 已結算，總計 ${total_amount_i} (個人用電: ${personal_amount}, 公共用電: ${shared_amount})。'
        })
        
    return True

@electricity_bp.route('/')
@login_required
@group_required
def list_bills():
    """電費帳單列表"""
    bills = ElectricityBill.get_by_group(current_user.group_id)
    members = User.get_by_group(current_user.group_id)
    
    bills_data = []
    for b in bills:
        readings = MeterReading.get_by_bill(b.id)
        splits = ElectricitySplit.get_by_bill(b.id)
        
        # 尋找目前使用者在該期帳單的分攤金額
        user_split = next((s for s in splits if s.user_id == current_user.id), None)
        
        bills_data.append({
            'info': b,
            'reading_count': len(readings),
            'total_members': len(members),
            'user_split': user_split,
            'is_settled': len(splits) > 0
        })
        
    return render_template('electricity/list.html', bills=bills_data)

@electricity_bp.route('/bill/new', methods=['GET', 'POST'])
@login_required
@group_required
def create_bill():
    """建立電費帳單"""
    if request.method == 'POST':
        total_amount_str = request.form.get('total_amount', '').strip()
        total_kwh_str = request.form.get('total_kwh', '').strip()
        period_start = request.form.get('period_start', '').strip()
        period_end = request.form.get('period_end', '').strip()
        
        if not total_amount_str or not total_kwh_str or not period_start or not period_end:
            flash('所有欄位皆為必填！', 'warning')
            return render_template('electricity/form.html', total_amount=total_amount_str, total_kwh=total_kwh_str, period_start=period_start, period_end=period_end)
            
        try:
            total_amount = float(total_amount_str)
            total_kwh = float(total_kwh_str)
            if total_amount <= 0 or total_kwh <= 0:
                raise ValueError()
        except ValueError:
            flash('請輸入有效的正數金額與度數！', 'warning')
            return render_template('electricity/form.html', total_amount=total_amount_str, total_kwh=total_kwh_str, period_start=period_start, period_end=period_end)
            
        bill_data = {
            'group_id': current_user.group_id,
            'total_amount': total_amount,
            'total_kwh': total_kwh,
            'period_start': period_start,
            'period_end': period_end,
            'created_by': current_user.id
        }
        
        new_bill = ElectricityBill.create(bill_data)
        if new_bill:
            # 發送通知給所有室友
            members = User.get_by_group(current_user.group_id)
            for m in members:
                Notification.create({
                    'user_id': m.id,
                    'group_id': current_user.group_id,
                    'type': 'electricity',
                    'title': '新電費帳單已登錄',
                    'message': f'管理員新增了計費期間為 {period_start} ~ {period_end} 的電費帳單，請登入並上傳您的房間電表度數。'
                })
            flash('電費帳單建立成功，已通知室友登錄度數！', 'success')
            return redirect(url_for('electricity.list_bills'))
        else:
            flash('建立帳單失敗，請重試。', 'danger')
            
    return render_template('electricity/form.html')

@electricity_bp.route('/bill/<int:bill_id>')
@login_required
@group_required
def detail(bill_id):
    """電費帳單詳情"""
    bill = ElectricityBill.get_by_id(bill_id)
    if not bill or bill.group_id != current_user.group_id:
        flash('找不到該帳單！', 'danger')
        return redirect(url_for('electricity.list_bills'))
        
    members = User.get_by_group(current_user.group_id)
    readings = MeterReading.get_by_bill(bill_id)
    splits = ElectricitySplit.get_by_bill(bill_id)
    
    # 映射為字典加速讀取
    readings_dict = {r.user_id: r for r in readings}
    splits_dict = {s.user_id: s for s in splits}
    members_dict = {m.id: m for m in members}
    
    # 整理成員名單、度數與分攤金額
    members_data = []
    for m in members:
        reading = readings_dict.get(m.id)
        split = splits_dict.get(m.id)
        members_data.append({
            'user': m,
            'reading': reading,
            'split': split
        })
        
    # 檢查當前使用者是否已登錄度數
    user_reading = readings_dict.get(current_user.id)
    user_split = splits_dict.get(current_user.id)
    
    return render_template(
        'electricity/detail.html',
        bill=bill,
        members=members_data,
        user_reading=user_reading,
        user_split=user_split,
        is_settled=len(splits) > 0
    )

@electricity_bp.route('/bill/<int:bill_id>/reading', methods=['GET', 'POST'])
@login_required
@group_required
def log_reading(bill_id):
    """登錄或編輯個人電表度數"""
    bill = ElectricityBill.get_by_id(bill_id)
    if not bill or bill.group_id != current_user.group_id:
        flash('找不到該帳單！', 'danger')
        return redirect(url_for('electricity.list_bills'))
        
    readings = MeterReading.get_by_bill(bill_id)
    user_reading = next((r for r in readings if r.user_id == current_user.id), None)
    
    if request.method == 'POST':
        start_str = request.form.get('start_reading', '').strip()
        end_str = request.form.get('end_reading', '').strip()
        
        if not start_str or not end_str:
            flash('起迄度數皆為必填！', 'warning')
            return render_template('electricity/meter_form.html', bill=bill, reading=user_reading)
            
        try:
            start_reading = float(start_str)
            end_reading = float(end_str)
            if start_reading < 0 or end_reading < start_reading:
                raise ValueError()
        except ValueError:
            flash('度數必須為大於 0 且結束度數不能小於起始度數！', 'warning')
            return render_template('electricity/meter_form.html', bill=bill, reading=user_reading, start_reading=start_str, end_reading=end_str)
            
        if user_reading:
            # 更新度數
            MeterReading.update(user_reading.id, {
                'start_reading': start_reading,
                'end_reading': end_reading
            })
            flash('個人電表度數更新成功！', 'success')
        else:
            # 新增度數
            MeterReading.create({
                'bill_id': bill_id,
                'user_id': current_user.id,
                'start_reading': start_reading,
                'end_reading': end_reading
            })
            flash('個人電表度數登錄成功！', 'success')
            
        # 自動檢查並更新分攤金額
        fully_calculated = calculate_electricity_splits_for_bill(bill_id)
        if fully_calculated:
            flash('所有室友皆已填寫度數，電費已自動結算完成！', 'success')
            
        return redirect(url_for('electricity.detail', bill_id=bill_id))
        
    return render_template('electricity/meter_form.html', bill=bill, reading=user_reading)

@electricity_bp.route('/bill/<int:bill_id>/pay', methods=['POST'])
@login_required
@group_required
def pay_bill(bill_id):
    """標記自己為已繳納電費"""
    splits = ElectricitySplit.get_by_bill(bill_id)
    user_split = next((s for s in splits if s.user_id == current_user.id), None)
    
    if not user_split:
        flash('尚未有您的分攤帳務！', 'warning')
        return redirect(url_for('electricity.detail', bill_id=bill_id))
        
    ElectricitySplit.update(user_split.id, {'is_paid': 1})
    flash('您已成功標記此期電費為已繳納！', 'success')
    return redirect(url_for('electricity.detail', bill_id=bill_id))

@electricity_bp.route('/bill/<int:bill_id>/delete', methods=['POST'])
@login_required
@group_required
def delete_bill(bill_id):
    """刪除電費帳單"""
    bill = ElectricityBill.get_by_id(bill_id)
    if not bill or bill.group_id != current_user.group_id:
        flash('找不到該帳單！', 'danger')
        return redirect(url_for('electricity.list_bills'))
        
    if bill.created_by != current_user.id and current_user.role != 'admin':
        flash('只有帳單建立者或群組管理員才能刪除此帳單！', 'danger')
        return redirect(url_for('electricity.detail', bill_id=bill_id))
        
    if ElectricityBill.delete(bill_id):
        flash('電費帳單已成功刪除！', 'info')
    else:
        flash('刪除帳單失敗，請重試。', 'danger')
        
    return redirect(url_for('electricity.list_bills'))
