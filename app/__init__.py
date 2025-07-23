from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from database.connection import init_app as init_db

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///victory_club.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    init_db(app)  # Initialize the database connection handler
    
    # Register routes
    from app.routes import init_app as routes_init_app
    routes_init_app(app)
    
    return app