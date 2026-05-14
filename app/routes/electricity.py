"""
智慧電費路由 — 帳單登錄、電表度數、分攤計算
Blueprint prefix: /electricity
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash

electricity_bp = Blueprint('electricity', __name__, url_prefix='/electricity')


@electricity_bp.route('', methods=['GET'])
def list_bills():
    """帳單列表
    - 處理：ElectricityBill.get_by_group(current_user.group_id)
    - 輸出：electricity/list.html
    """
    pass


@electricity_bp.route('/new', methods=['GET'])
def new_page():
    """新增帳單頁面
    - 輸出：electricity/form.html
    """
    pass


@electricity_bp.route('', methods=['POST'])
def create():
    """新增帳單處理
    - 輸入：total_amount, total_kwh, period_start, period_end
    - 處理：ElectricityBill.create()
    - 輸出：重導向 /electricity/<id>/meter
    """
    pass


@electricity_bp.route('/<int:id>', methods=['GET'])
def detail(id):
    """帳單詳情
    - 輸入：URL 參數 id
    - 處理：取得帳單、電表度數、分攤結果
    - 輸出：electricity/detail.html
    - 錯誤：不存在 → 404
    """
    pass


@electricity_bp.route('/<int:id>/meter', methods=['GET'])
def meter_page(id):
    """登錄電表頁面
    - 輸入：URL 參數 id
    - 輸出：electricity/meter_form.html
    - 錯誤：不存在 → 404
    """
    pass


@electricity_bp.route('/<int:id>/meter', methods=['POST'])
def meter_submit(id):
    """登錄電表處理
    - 輸入：URL 參數 id；表單 start_reading, end_reading
    - 處理：MeterReading.create() → 若全部填完則計算分攤 → ElectricitySplit.create()
    - 輸出：重導向 /electricity/<id>
    - 錯誤：已登錄 → 提示；度數不合理 → 回到表單
    """
    pass
