"""
Routes 套件初始化
註冊所有 Blueprint 到 Flask App
"""


def register_blueprints(app):
    """將所有 Blueprint 註冊到 Flask App"""
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.group import group_bp
    from app.routes.agreement import agreement_bp
    from app.routes.expense import expense_bp
    from app.routes.electricity import electricity_bp
    from app.routes.chore import chore_bp
    from app.routes.reminder import reminder_bp
    from app.routes.inventory import inventory_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(group_bp)
    app.register_blueprint(agreement_bp)
    app.register_blueprint(expense_bp)
    app.register_blueprint(electricity_bp)
    app.register_blueprint(chore_bp)
    app.register_blueprint(reminder_bp)
    app.register_blueprint(inventory_bp)
