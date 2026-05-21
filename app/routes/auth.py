from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import user as user_model
from app.utils.auth_helpers import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        nickname = request.form.get('nickname', '').strip()
        
        # 驗證必填欄位
        if not email or not password or not nickname:
            flash("請填寫所有必填欄位！", "danger")
            return render_template('auth/register.html')
            
        if password != confirm_password:
            flash("兩次輸入的密碼不一致！", "danger")
            return render_template('auth/register.html')
            
        # 檢查 Email 是否已註冊
        existing_user = user_model.get_by_email(email)
        if existing_user:
            flash("此 Email 已被註冊！", "danger")
            return render_template('auth/register.html')
            
        # 密碼雜湊與建立
        hashed_password = generate_password_hash(password)
        try:
            user_model.create({
                'email': email,
                'password_hash': hashed_password,
                'nickname': nickname,
                'role': 'member',
                'group_id': None
            })
            flash("註冊成功！請登入您的帳號。", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f"註冊失敗，資料庫錯誤：{e}", "danger")
            return render_template('auth/register.html')
            
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash("請輸入帳號與密碼！", "danger")
            return render_template('auth/login.html')
            
        db_user = user_model.get_by_email(email)
        if not db_user or not check_password_hash(db_user['password_hash'], password):
            flash("帳號或密碼錯誤！", "danger")
            return render_template('auth/login.html')
            
        # 成功登入
        user_obj = User(db_user['id'], db_user['email'], db_user['nickname'], db_user['role'], db_user['group_id'])
        login_user(user_obj)
        flash("歡迎回來！", "success")
        return redirect(url_for('dashboard.index'))
        
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("您已成功登出。", "success")
    return redirect(url_for('auth.login'))
