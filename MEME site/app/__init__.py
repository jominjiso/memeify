from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.extentions import bcrypt

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.secret_key = '5df0312afecb6e105f83d421e67762f4'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./meme.db'
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    
    migrate = Migrate()
    migrate.init_app(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "You must be logged in to view this content."
    login_manager.login_message_category = "warning"

    from app.models import User
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(id)

    # Import and register blueprints INSIDE create_app
    from app.routes.home import home
    from app.routes.auth import auth

    app.register_blueprint(home)
    app.register_blueprint(auth, url_prefix='/auth')

    return app