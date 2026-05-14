from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from app.models.electricity import Bill, Room, MeterRecord
from app import db

bp = Blueprint('electricity', __name__, url_prefix='/electricity')

@bp.route('/')
def dashboard():
    bills = Bill.query.order_by(Bill.period_start.desc()).all()
    rooms = Room.query.all()
    unpaid_records = MeterRecord.query.filter_by(is_paid=False).all()
    return render_template('electricity/dashboard.html', bills=bills, rooms=rooms, unpaid_records=unpaid_records)

@bp.route('/estimate')
def estimate():
    return render_template('electricity/estimate.html')

@bp.route('/bill/new', methods=('GET', 'POST'))
def new_bill():
    rooms = Room.query.all()
    if request.method == 'POST':
        try:
            period_start = datetime.strptime(request.form['period_start'], '%Y-%m-%d').date()
            period_end = datetime.strptime(request.form['period_end'], '%Y-%m-%d').date()
            total_amount = float(request.form['total_amount'])
            total_degrees = float(request.form['total_degrees'])
            
            # 建立新帳單
            bill = Bill(
                period_start=period_start,
                period_end=period_end,
                total_amount=total_amount,
                total_degrees=total_degrees,
                public_amount=0 # 先填 0，稍後計算
            )
            db.session.add(bill)
            db.session.flush() # 取得 bill.id
            
            # 收集各房間資料
            total_personal_degrees = 0
            room_records = []
            
            for room in rooms:
                start_deg = float(request.form[f'start_degree_{room.id}'])
                end_deg = float(request.form[f'end_degree_{room.id}'])
                used_deg = end_deg - start_deg
                if used_deg < 0:
                    flash(f'{room.name} 的結束度數不能小於起始度數', 'danger')
                    db.session.rollback()
                    return render_template('electricity/new_bill.html', rooms=rooms)
                
                total_personal_degrees += used_deg
                room_records.append({
                    'room_id': room.id,
                    'start_degree': start_deg,
                    'end_degree': end_deg,
                    'used_degree': used_deg
                })
            
            if total_personal_degrees > total_degrees:
                flash('各房間用電加總不能大於總度數', 'danger')
                db.session.rollback()
                return render_template('electricity/new_bill.html', rooms=rooms)
                
            # 計算單價與公共用電
            unit_price = total_amount / total_degrees if total_degrees > 0 else 0
            public_degrees = total_degrees - total_personal_degrees
            public_amount = public_degrees * unit_price
            bill.public_amount = public_amount
            
            # 分攤公共用電給各房間 (假設均攤)
            public_shared_amount = public_amount / len(rooms) if rooms else 0
            
            for record in room_records:
                personal_amount = record['used_degree'] * unit_price
                meter_record = MeterRecord(
                    bill_id=bill.id,
                    room_id=record['room_id'],
                    start_degree=record['start_degree'],
                    end_degree=record['end_degree'],
                    personal_amount=personal_amount,
                    public_shared_amount=public_shared_amount,
                    is_paid=False
                )
                db.session.add(meter_record)
                
            db.session.commit()
            flash('電費帳單已成功建立並完成分攤計算', 'success')
            return redirect(url_for('electricity.dashboard'))
            
        except ValueError:
            flash('輸入格式錯誤，請確認所有欄位都是有效的數字或日期', 'danger')
            db.session.rollback()
            
    return render_template('electricity/new_bill.html', rooms=rooms)

@bp.route('/bill/<int:id>/pay', methods=('POST',))
def pay_bill(id):
    record = MeterRecord.query.get_or_404(id)
    record.is_paid = True
    db.session.commit()
    flash(f'已標記 {record.room.name} 繳費完成', 'success')
    return redirect(url_for('electricity.dashboard'))
