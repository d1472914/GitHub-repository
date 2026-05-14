"""
身份驗證路由 — 註冊、登入、登出
Blueprint prefix: /auth
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET'])
def register_page():
    """顯示註冊表單頁面
    - 輸出：auth/register.html
    - 若已登入，重導向 /dashboard
    """
    pass


@auth_bp.route('/register', methods=['POST'])
def register():
    """處理註冊表單
    - 輸入：email, password, confirm_password, nickname
    - 處理：驗證資料 → 檢查 Email 不重複 → 密碼雜湊 → User.create()
    - 輸出：成功 → 重導向登入頁；失敗 → 回到註冊頁
    """
    pass


@auth_bp.route('/login', methods=['GET'])
def login_page():
    """顯示登入表單頁面
    - 輸出：auth/login.html
    - 若已登入，重導向 /dashboard
    """
    pass


@auth_bp.route('/login', methods=['POST'])
def login():
    """處理登入表單
    - 輸入：email, password
    - 處理：User.get_by_email() → 驗證密碼 → login_user()
    - 輸出：成功 → 重導向 /dashboard；失敗 → 回到登入頁
    """
    pass


@auth_bp.route('/logout', methods=['GET'])
def logout():
    """登出
    - 處理：logout_user() 清除 session
    - 輸出：重導向 /auth/login
    """
    pass
