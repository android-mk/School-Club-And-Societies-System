from flask import current_app
from database.connection import get_db_connection

class ClubDAO:
    def get_all_clubs(self):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clubs")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            current_app.logger.error(f"Error getting all clubs: {e}")
            raise

    def get_club_choices(self):
        try:
            clubs = self.get_all_clubs()
            return [(c['club_id'], c['name']) for c in clubs]
        except Exception as e:
            current_app.logger.error(f"Error getting club choices: {e}")
            raise

    def get_club(self, club_id):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clubs WHERE club_id = ?", (club_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            current_app.logger.error(f"Error getting club: {e}")
            raise

    def get_club_fee(self, club_id):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT fee_amount FROM clubs WHERE club_id = ?", (club_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            current_app.logger.error(f"Error getting club fee: {e}")
            raise

    def get_all_clubs_with_stats(self):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, 
                       COUNT(m.membership_id) as member_count,
                       p.name as patron_name
                FROM clubs c
                LEFT JOIN memberships m ON c.club_id = m.club_id AND m.is_active = 1
                LEFT JOIN patrons p ON c.patron_id = p.patron_id
                GROUP BY c.club_id
            """)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            current_app.logger.error(f"Error getting clubs with stats: {e}")
            raise

    def get_club_with_details(self, club_id):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Get basic club info
            cursor.execute("""
                SELECT c.*, p.name as patron_name
                FROM clubs c
                LEFT JOIN patrons p ON c.patron_id = p.patron_id
                WHERE c.club_id = ?
            """, (club_id,))
            row = cursor.fetchone()
            club = dict(row) if row else None
            
            if club:
                # Get leadership
                cursor.execute("""
                    SELECT s.student_id, s.name, m.role
                    FROM memberships m
                    JOIN students s ON m.student_id = s.student_id
                    WHERE m.club_id = ? AND m.is_active = 1
                    AND m.role IN ('Chairperson', 'Vice Chairperson', 'Secretary', 'Treasurer')
                """, (club_id,))
                club['leadership'] = [dict(row) for row in cursor.fetchall()]
                
                # Get active members
                cursor.execute("""
                    SELECT s.student_id, s.name, s.class, m.role, m.joined_date
                    FROM memberships m
                    JOIN students s ON m.student_id = s.student_id
                    WHERE m.club_id = ? AND m.is_active = 1
                    ORDER BY m.role != 'Member', s.name
                """, (club_id,))
                club['members'] = [dict(row) for row in cursor.fetchall()]
            
            return club
        except Exception as e:
            current_app.logger.error(f"Error getting club details: {e}")
            raise

    def assign_patron(self, club_id, patron_id):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE clubs SET patron_id = ? 
                WHERE club_id = ?
            """, (patron_id, club_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            current_app.logger.error(f"Error assigning patron: {e}")
            raise

    def get_clubs_summary(self):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.club_id, c.name, COUNT(m.membership_id) as member_count, SUM(c.fee_amount) as total_fees
                FROM clubs c
                LEFT JOIN memberships m ON c.club_id = m.club_id AND m.is_active = 1
                GROUP BY c.club_id, c.name
            """)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            current_app.logger.error(f"Error getting clubs summary: {e}")
            raise