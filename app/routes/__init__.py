from flask import Flask

def register_blueprints(app: Flask):
    """註冊所有的 Flask Blueprints"""
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.group import group_bp
    from app.routes.agreement import agreement_bp
    from app.routes.expense import expense_bp
    from app.routes.electricity import electricity_bp
    from app.routes.chore import chore_bp
    from app.routes.reminder import reminder_bp
    from app.routes.inventory import inventory_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(group_bp, url_prefix='/group')
    app.register_blueprint(agreement_bp, url_prefix='/agreement')
    app.register_blueprint(expense_bp, url_prefix='/expense')
    app.register_blueprint(electricity_bp, url_prefix='/electricity')
    app.register_blueprint(chore_bp, url_prefix='/chore')
    app.register_blueprint(reminder_bp, url_prefix='/reminder')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
