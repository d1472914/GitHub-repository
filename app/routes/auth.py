from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET'])
def register_page():
    """顯示註冊表單頁面"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard_page'))
    return render_template('auth/register.html')


@auth_bp.route('/register', methods=['POST'])
def register():
    """處理註冊表單"""
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    nickname = request.form.get('nickname')

    if not email or not password or not nickname:
        flash('請填寫所有必填欄位。', 'danger')
        return redirect(url_for('auth.register_page'))

    if password != confirm_password:
        flash('密碼與確認密碼不符。', 'danger')
        return redirect(url_for('auth.register_page'))

    existing_user = User.get_by_email(email)
    if existing_user:
        flash('該 Email 已被註冊，請換一個或直接登入。', 'danger')
        return redirect(url_for('auth.register_page'))

    # 使用密碼哈希
    password_hash = generate_password_hash(password)
    User.create(email=email, password_hash=password_hash, nickname=nickname)
    
    flash('註冊成功！請登入。', 'success')
    return redirect(url_for('auth.login_page'))


@auth_bp.route('/login', methods=['GET'])
def login_page():
    """顯示登入表單頁面"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard_page'))
    return render_template('auth/login.html')


@auth_bp.route('/login', methods=['POST'])
def login():
    """處理登入表單"""
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        flash('請輸入 Email 與密碼。', 'danger')
        return redirect(url_for('auth.login_page'))

    user = User.get_by_email(email)
    if not user or not check_password_hash(user.password_hash, password):
        flash('密碼錯誤或此 Email 尚未註冊。', 'danger')
        return redirect(url_for('auth.login_page'))

    login_user(user)
    flash('登入成功，歡迎回來！', 'success')
    return redirect(url_for('dashboard.dashboard_page'))


@auth_bp.route('/logout', methods=['GET'])
def logout():
    """登出"""
    logout_user()
    flash('您已登出系統。', 'success')
    return redirect(url_for('auth.login_page'))
