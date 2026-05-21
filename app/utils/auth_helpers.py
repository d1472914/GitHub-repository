from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def login_required(f):
    """
    登入驗證裝飾器，確保使用者已登入才可存取路由。
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("請先登入系統。", "warning")
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated_function
