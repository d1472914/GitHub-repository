from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
from app.models.group import Group

def group_required(f):
    """裝飾器：要求使用者必須已加入群組"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login_page'))
        if not current_user.group_id:
            flash('請先建立或加入一個室友群組！', 'warning')
            return redirect(url_for('group.group_home'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """裝飾器：要求使用者必須是群組的管理員"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login_page'))
        if not current_user.group_id:
            flash('請先建立或加入一個室友群組！', 'warning')
            return redirect(url_for('group.group_home'))
        
        group = Group.get_by_id(current_user.group_id)
        if not group or group.created_by != current_user.id:
            flash('此操作需要群組管理員權限！', 'danger')
            # 導回儀表板
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function
