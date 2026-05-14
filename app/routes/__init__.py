from flask import Blueprint, render_template

bp = Blueprint('electricity', __name__, url_prefix='/electricity')

@bp.route('/')
def index():
    # 預設首頁導向即時估算
    return render_template('electricity/estimate.html')

@bp.route('/estimate')
def estimate():
    return render_template('electricity/estimate.html')
