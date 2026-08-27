import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.extentions import bcrypt

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '5df0312afecb6e105f83d421e67762f4'
    
    # Configure upload folder path
    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder
    
    
    # Check for Render's DATABASE_URL first; fall back to SQLite for local development
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Fix Render's legacy 'postgres://' prefix for SQLAlchemy compatibility
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./meme.db'
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    
    migrate = Migrate()
    migrate.init_app(app, db)

    # Import and register only the home blueprint
    from app.routes.home import home
    app.register_blueprint(home)

    # Create database tables automatically on startup
    with app.app_context():
        db.create_all()

    return app