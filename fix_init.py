content = '''from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    from app.commands import init_db_command
    app.cli.add_command(init_db_command)

    from app.routes import main
    app.register_blueprint(main.bp)

    from app.routes import shop
    app.register_blueprint(shop.bp)

    from app.routes import admin
    app.register_blueprint(admin.bp)

    from app.routes import auth
    app.register_blueprint(auth.bp)

    with app.app_context():
        db.create_all()

    return app'''

with open('app/__init__.py', 'w', encoding='utf-8') as f:
    f.write(content)