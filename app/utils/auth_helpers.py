<<<<<<< HEAD
"""
認證輔助工具 (Auth Helpers)
提供登入驗證裝飾器、密碼雜湊工具等
"""
=======
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import UserMixin, current_user
from app.models.user import get_by_id

class User(UserMixin):
    def __init__(self, id, email, nickname, role, group_id):
        self.id = id
        self.email = email
        self.nickname = nickname
        self.role = role
        self.group_id = group_id

def load_user_object(user_id):
    """供 Flask-Login 使用的用戶加載器"""
    u = get_by_id(int(user_id))
    if u:
        return User(u['id'], u['email'], u['nickname'], u['role'], u['group_id'])
    return None

def group_required(f):
    """裝飾器：限制使用者必須先登入，且必須已加入群組才可訪問"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.group_id:
            flash("請先建立或加入一個室友群組！", "warning")
            return redirect(url_for('group.join'))
        return f(*args, **kwargs)
    return decorated_function
>>>>>>> 1e48de0edac6544d863f36aadea0f725405e001b
