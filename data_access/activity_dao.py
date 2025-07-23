from flask import current_app
from database.connection import get_db_connection

class ActivityDAO:
    def get_recent_activities(self, limit=5):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM club_activities 
                ORDER BY activity_date DESC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            current_app.logger.error(f"Error getting recent activities: {e}")
            raise

    def get_all_activities(self):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.*, c.name as club_name 
                FROM club_activities a
                JOIN clubs c ON a.club_id = c.club_id
                ORDER BY a.activity_date DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            current_app.logger.error(f"Error getting all activities: {e}")
            raise

    def get_past_activities(self, club_id):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM club_activities 
                WHERE club_id = ? AND activity_date <= date('now')
                ORDER BY activity_date DESC
            """, (club_id,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            current_app.logger.error(f"Error getting past activities: {e}")
            raise

    def get_upcoming_activities(self, club_id):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM club_activities 
                WHERE club_id = ? AND activity_date > date('now')
                ORDER BY activity_date ASC
            """, (club_id,))
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            current_app.logger.error(f"Error getting upcoming activities: {e}")
            raise

    def log_activity_with_allocations(self, club_id, activity_name, activity_date, revenue, allocations, school_contribution):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Log the activity
            cursor.execute("""
                INSERT INTO club_activities (club_id, activity_name, activity_date, revenue)
                VALUES (?, ?, ?, ?)
            """, (club_id, activity_name, activity_date, revenue))
            
            # Record financial allocations
            for purpose, amount in allocations.items():
                cursor.execute("""
                    INSERT INTO finances (club_id, amount, transaction_type, description, transaction_date)
                    VALUES (?, ?, 'Revenue Allocation', ?, ?)
                """, (club_id, amount, f"50% for {purpose}", activity_date))
            
            # Record school contribution
            if school_contribution > 0:
                cursor.execute("""
                    INSERT INTO finances (club_id, amount, transaction_type, description, transaction_date)
                    VALUES (?, ?, 'School Contribution', 'Party contribution', ?)
                """, (club_id, school_contribution, activity_date))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            current_app.logger.error(f"Error logging activity: {e}")
            raise