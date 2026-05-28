"""
身份驗證路由 — 註冊、登入、登出
Blueprint prefix: /auth
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(f):
    """
    登入驗證裝飾器，確保使用者已登入才可存取路由。
    支援 Flask-Login 與 g.user / session['user_id'] 的混合相容。
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            user_id = session.get('user_id')
            if user_id:
                user = User.get_by_id(user_id)
                if user:
                    login_user(user)
                    g.user = user
                    return f(*args, **kwargs)
            flash("請先登入系統！", "warning")
            return redirect(url_for('auth.login_page'))
        
        g.user = current_user
        if 'user_id' not in session:
            session['user_id'] = current_user.id
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET'])
def register_page():
    """顯示註冊表單頁面"""
    if current_user.is_authenticated or 'user_id' in session:
        return redirect(url_for('dashboard.dashboard_page'))
    return render_template('auth/register.html')

@auth_bp.route('/register', methods=['POST'])
def register():
    """處理註冊表單"""
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    nickname = request.form.get('nickname', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()

    if not email or not password or not nickname:
        flash("所有必填欄位皆不可為空！", "error")
        return render_template('auth/register.html')

    if len(password) < 6:
        flash("密碼長度必須至少為 6 位字元！", "error")
        return render_template('auth/register.html')

    if confirm_password and password != confirm_password:
        flash("兩次輸入的密碼不一致！", "error")
        return render_template('auth/register.html')

    try:
        existing_user = User.get_by_email(email)
        if existing_user:
            flash("此電子信箱已被註冊！", "error")
            return render_template('auth/register.html')

        password_hash = generate_password_hash(password)
        # 呼叫 User.create。此處會傳回 User 實例 (使用關鍵字引數)
        user = User.create(
            email=email,
            password_hash=password_hash,
            nickname=nickname,
            role='member',
            group_id=None
        )
        
        if user:
            flash("註冊成功！請登入您的帳號。", "success")
            return redirect(url_for('auth.login_page'))
        else:
            flash("註冊失敗，請稍後再試。", "error")
            return render_template('auth/register.html')

    except Exception as e:
        print(f"Error during registration route: {e}")
        flash("伺服器錯誤，請聯絡管理員。", "error")
        return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET'])
def login_page():
    """顯示登入表單頁面"""
    if current_user.is_authenticated or 'user_id' in session:
        return redirect(url_for('dashboard.dashboard_page'))
    return render_template('auth/login.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    """處理登入表單"""
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()

    if not email or not password:
        flash("請輸入電子信箱與密碼！", "error")
        return render_template('auth/login.html')

    try:
        user = User.get_by_email(email)
        if not user or not check_password_hash(user.password_hash, password):
            flash("帳號或密碼錯誤！", "error")
            return render_template('auth/login.html')

        # 登入成功，設定 session 與 flask_login
        login_user(user)
        session['user_id'] = user.id
        g.user = user
        flash(f"歡迎回來，{user.nickname}！", "success")
        return redirect(url_for('dashboard.dashboard_page'))

    except Exception as e:
        print(f"Error during login route: {e}")
        flash("伺服器錯誤，請聯絡管理員。", "error")
        return render_template('auth/login.html')

@auth_bp.route('/logout', methods=['GET'])
def logout():
    """登出"""
    logout_user()
    session.clear()
    flash("您已成功登出。", "info")
    return redirect(url_for('auth.login_page'))
