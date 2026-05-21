"""
身份驗證路由 — 註冊、登入、登出
Blueprint prefix: /auth
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def get_current_user():
    """從 session 中取得目前登入的使用者資料"""
    if 'user_id' not in session:
        return None
    return User.get_by_id(session['user_id'])

def login_required(f):
    """驗證登入狀態的裝飾器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("請先登入系統！", "warning")
            return redirect(url_for('auth.login_page'))
        g.user = User.get_by_id(session['user_id'])
        if not g.user:
            session.pop('user_id', None)
            flash("登入工作階段已失效，請重新登入。", "warning")
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET'])
def register_page():
    """顯示註冊表單頁面
    - 輸出：auth/register.html
    - 若已登入，重導向 /dashboard
    """
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    return render_template('auth/register.html')

@auth_bp.route('/register', methods=['POST'])
def register():
    """處理註冊表單
    - 輸入：email, password, confirm_password (選填), nickname
    - 處理：驗證資料 → 檢查 Email 不重複 → 密碼雜湊 → User.create()
    - 輸出：成功 → 重導向登入頁；失敗 → 回到註冊頁
    """
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    nickname = request.form.get('nickname', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()

    # 1. 基本輸入驗證
    if not email or not password or not nickname:
        flash("所有必填欄位皆不可為空！", "error")
        return render_template('auth/register.html')

    # 2. 密碼長度驗證
    if len(password) < 6:
        flash("密碼長度必須至少為 6 位字元！", "error")
        return render_template('auth/register.html')

    # 3. 如果表單提供了 confirm_password，則驗證是否一致
    if confirm_password and password != confirm_password:
        flash("兩次輸入的密碼不一致！", "error")
        return render_template('auth/register.html')

    try:
        # 4. 檢查 Email 是否已重複
        existing_user = User.get_by_email(email)
        if existing_user:
            flash("此電子信箱已被註冊！", "error")
            return render_template('auth/register.html')

        # 5. 密碼雜湊與建立使用者
        password_hash = generate_password_hash(password)
        user_data = {
            'email': email,
            'password_hash': password_hash,
            'nickname': nickname,
            'role': 'member',
            'group_id': None
        }
        
        user_id = User.create(user_data)
        if user_id:
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
    """顯示登入表單頁面
    - 輸出：auth/login.html
    - 若已登入，重導向 /dashboard
    """
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    return render_template('auth/login.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    """處理登入表單
    - 輸入：email, password
    - 處理：User.get_by_email() → 驗證密碼 → login_user()
    - 輸出：成功 → 重導向 /dashboard；失敗 → 回到登入頁
    """
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()

    # 1. 基本輸入驗證
    if not email or not password:
        flash("請輸入電子信箱與密碼！", "error")
        return render_template('auth/login.html')

    try:
        # 2. 取得使用者記錄
        user = User.get_by_email(email)
        if not user:
            flash("帳號或密碼錯誤！", "error")
            return render_template('auth/login.html')

        # 3. 驗證密碼雜湊
        if not check_password_hash(user['password_hash'], password):
            flash("帳號或密碼錯誤！", "error")
            return render_template('auth/login.html')

        # 4. 登入成功，儲存 session
        session['user_id'] = user['id']
        flash(f"歡迎回來，{user['nickname']}！", "success")
        return redirect(url_for('dashboard.index'))

    except Exception as e:
        print(f"Error during login route: {e}")
        flash("伺服器錯誤，請聯絡管理員。", "error")
        return render_template('auth/login.html')

@auth_bp.route('/logout', methods=['GET'])
def logout():
    """登出
    - 處理：清除 session
    - 輸出：重導向 /auth/login
    """
    session.clear()
    flash("您已成功登出。", "info")
    return redirect(url_for('auth.login_page'))
