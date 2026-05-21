from flask import Blueprint, render_template

bp = Blueprint('electricity', __name__, url_prefix='/electricity')

@bp.route('/')
def index():
    # 預設首頁導向即時估算
    return render_template('electricity/estimate.html')

@bp.route('/estimate')
def estimate():
    return render_template('electricity/estimate.html')
from .auth import auth_bp
from .dashboard import dashboard_bp
from .group import group_bp
from .agreement import agreement_bp
from .expense import expense_bp
from .electricity import electricity_bp
from .chore import chore_bp
from .reminder import reminder_bp
from .inventory import inventory_bp

def register_blueprints(app):
    """將所有 Blueprint 註冊到 Flask app 實例"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(group_bp)
    app.register_blueprint(agreement_bp)
    app.register_blueprint(expense_bp)
    app.register_blueprint(electricity_bp)
    app.register_blueprint(chore_bp)
    app.register_blueprint(reminder_bp)
    app.register_blueprint(inventory_bp)
