from flask import current_app
from database.connection import get_db_connection

class PatronDAO:
    def get_all_patrons(self):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patrons")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            current_app.logger.error(f"Error getting all patrons: {e}")
            raise

    def add_patron(self, name, email):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO patrons (name, email) VALUES (?, ?)",
                (name, email)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            current_app.logger.error(f"Error adding patron: {e}")
            raise