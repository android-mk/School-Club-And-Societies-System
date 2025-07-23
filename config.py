import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'victory_club.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False