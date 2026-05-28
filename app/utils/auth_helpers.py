"""
認證輔助工具 (Auth Helpers)
提供登入驗證裝飾器、密碼雜湊工具等。
"""

from functools import wraps
from flask import redirect, url_for, flash, g, session
from flask_login import current_user
from app.models.user import User

def login_required(f):
    """
    登入驗證裝飾器，確保使用者已登入才可存取路由。
    支援 Flask-Login 與 g.user / session['user_id'] 的混合相容。
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 優先檢查 Flask-Login current_user
        if not current_user.is_authenticated:
            # 備用檢查：如果 session['user_id'] 存在，嘗試手動登入
            user_id = session.get('user_id')
            if user_id:
                user = User.get_by_id(user_id)
                if user:
                    from flask_login import login_user
                    login_user(user)
                    g.user = user
                    return f(*args, **kwargs)
            
            flash("請先登入系統。", "warning")
            return redirect(url_for('auth.login_page'))
        
        # 確保 g.user 已經設定，方便 sqlite3 模組存取
        g.user = current_user
        if 'user_id' not in session:
            session['user_id'] = current_user.id
            
        return f(*args, **kwargs)
    return decorated_function
