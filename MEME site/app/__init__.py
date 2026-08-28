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
    
    # Fetch DATABASE_URL from Render env, or fallback directly to your Render DB string locally
    DATABASE_URL = os.environ.get('DATABASE_URL') or "postgresql://memefiy_user:mT5T7LhfeOVS6GRsQq1MJcXlmUo0Z4VN@dpg-da6jdqv10e5c73bu41t0-a.oregon-postgres.render.com/memefiy"

    # Fix legacy postgres:// prefix for SQLAlchemy compatibility
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        
    # Assign the final DATABASE_URL unconditionally
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    
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