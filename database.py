from models import db, User, Document
from flask import Flask

def init_db(app):
    with app.app_context():
        try:
            db.create_all()
            print("[OK] Database initialized successfully!")
        except Exception as e:
            print(f"[ERROR] Database initialization error: {e}")