
"""
Database migration to add chat history tables
"""
from app import app
from models import db

def create_chat_tables():
    """Creates chat tables in the database"""
    with app.app_context():
        # Create tables
        db.create_all()
        print("Chat history tables created successfully")

if __name__ == "__main__":
    create_chat_tables()
