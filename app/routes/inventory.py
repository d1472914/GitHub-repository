from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.utils.auth_helpers import login_required

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@inventory_bp.route('/', methods=['GET'])
@login_required
def inventory_list():
    """物資清單"""
    return render_template('inventory/list.html')

@inventory_bp.route('/<int:item_id>', methods=['GET'])
@login_required
def inventory_detail(item_id):
    """物資詳情 (入出庫歷史)"""
    return render_template('inventory/detail.html', item_id=item_id)

@inventory_bp.route('/add', methods=['GET', 'POST'])
@inventory_bp.route('/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def inventory_form(item_id=None):
    """新增 / 編輯物資表單"""
    if request.method == 'POST':
        pass
    return render_template('inventory/form.html', item_id=item_id)
