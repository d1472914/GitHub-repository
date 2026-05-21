from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register_page():
    """註冊頁面"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        nickname = request.form.get('nickname', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        # 基本驗證
        if not email or not nickname or not password or not confirm_password:
            flash('所有欄位皆為必填！', 'warning')
            return render_template('auth/register.html', email=email, nickname=nickname)
            
        if password != confirm_password:
            flash('密碼與確認密碼不一致！', 'warning')
            return render_template('auth/register.html', email=email, nickname=nickname)
            
        # 檢查 Email 是否已被註冊
        existing_user = User.get_by_email(email)
        if existing_user:
            flash('該 Email 已被註冊！', 'warning')
            return render_template('auth/register.html', email=email, nickname=nickname)
            
        # 建立使用者
        password_hash = generate_password_hash(password)
        user_data = {
            'email': email,
            'nickname': nickname,
            'password_hash': password_hash,
            'role': 'member',
            'group_id': None
        }
        
        new_user = User.create(user_data)
        if new_user:
            flash('註冊成功！請登入。', 'success')
            return redirect(url_for('auth.login_page'))
        else:
            flash('註冊失敗，請稍後再試。', 'danger')
            return render_template('auth/register.html', email=email, nickname=nickname)
            
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    """登入頁面"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not email or not password:
            flash('請輸入 Email 與密碼！', 'warning')
            return render_template('auth/login.html', email=email)
            
        user = User.get_by_email(email)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f'歡迎回來，{user.nickname}！', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Email 或密碼錯誤！', 'danger')
            return render_template('auth/login.html', email=email)
            
    return render_template('auth/login.html')

@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """登出"""
    logout_user()
    flash('您已成功登出。', 'success')
    return redirect(url_for('auth.login_page'))
