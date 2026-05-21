"""
共同物資庫存路由 — 物資 CRUD、入庫、出庫
Blueprint prefix: /inventory
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')


@inventory_bp.route('', methods=['GET'])
def list_items():
    """物資清單
    - 處理：InventoryItem.get_by_group(current_user.group_id)
    - 輸出：inventory/list.html
    """
    pass


@inventory_bp.route('/new', methods=['GET'])
def new_page():
    """新增物資頁面
    - 輸出：inventory/form.html（空白表單，mode='create'）
    """
    pass


@inventory_bp.route('', methods=['POST'])
def create():
    """新增物資處理
    - 輸入：name, unit, quantity, min_quantity
    - 處理：InventoryItem.create()
    - 輸出：重導向 /inventory
    """
    pass


@inventory_bp.route('/<int:id>', methods=['GET'])
def detail(id):
    """物資詳情
    - 輸入：URL 參數 id
    - 處理：取得物資與入出庫歷史 InventoryLog.get_by_item()
    - 輸出：inventory/detail.html
    - 錯誤：不存在 → 404
    """
    pass


@inventory_bp.route('/<int:id>/edit', methods=['GET'])
def edit_page(id):
    """編輯物資頁面
    - 輸入：URL 參數 id
    - 輸出：inventory/form.html（預填資料，mode='edit'）
    - 錯誤：不存在 → 404
    """
    pass


@inventory_bp.route('/<int:id>/update', methods=['POST'])
def update(id):
    """更新物資
    - 輸入：URL 參數 id；表單 name, unit, min_quantity
    - 處理：item.update()
    - 輸出：重導向 /inventory/<id>
    - 錯誤：不存在 → 404
    """
    pass


@inventory_bp.route('/<int:id>/stock-in', methods=['POST'])
def stock_in(id):
    """入庫登記
    - 輸入：URL 參數 id；表單 quantity, note, sync_expense
    - 處理：item.stock_in() → InventoryLog.create('stock_in') → 可選同步帳本
    - 輸出：重導向 /inventory/<id>
    - 錯誤：不存在 → 404；數量非正整數
    """
    pass


@inventory_bp.route('/<int:id>/stock-out', methods=['POST'])
def stock_out(id):
    """出庫登記
    - 輸入：URL 參數 id；表單 quantity, note
    - 處理：item.stock_out() → InventoryLog.create('stock_out') → 低庫存通知
    - 輸出：重導向 /inventory/<id>
    - 錯誤：不存在 → 404；數量非正整數
    """
    pass
