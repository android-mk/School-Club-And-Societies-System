from flask import current_app
from database.connection import get_db_connection

class MembershipDAO:
    def get_membership(self, membership_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.*, s.name as student_name, s.student_id, c.name as club_name
            FROM memberships m
            JOIN students s ON m.student_id = s.student_id
            JOIN clubs c ON m.club_id = c.club_id
            WHERE m.membership_id = ?
        """, (membership_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def is_student_in_club(self, student_id, club_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 1 FROM memberships 
            WHERE student_id = ? AND club_id = ? AND is_active = 1
        """, (student_id, club_id))
        return cursor.fetchone() is not None

    def create_membership(self, student_id, club_id, role='Member'):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO memberships 
                (student_id, club_id, role, joined_date, is_active)
                VALUES (?, ?, ?, date('now'), 1)
            """, (student_id, club_id, role))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            current_app.logger.error(f"Error creating membership: {e}")
            raise

    def deactivate_membership(self, membership_id):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE memberships SET is_active = 0 
                WHERE membership_id = ?
            """, (membership_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            current_app.logger.error(f"Error deactivating membership: {e}")
            raise

    def log_approval(self, membership_id, approval_notes):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO exit_requests 
                (membership_id, approved, approval_notes, approval_date)
                VALUES (?, 1, ?, date('now'))
            """, (membership_id, approval_notes))
            conn.commit()
        except Exception as e:
            conn.rollback()
            current_app.logger.error(f"Error logging approval: {e}")
            raise

    def get_pending_approvals(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.membership_id, s.student_id, s.name as student_name, 
                   c.name as club_name, c.club_id
            FROM memberships m
            JOIN students s ON m.student_id = s.student_id
            JOIN clubs c ON m.club_id = c.club_id
            WHERE m.role != 'Member' AND m.is_active = 1
            AND m.membership_id IN (
                SELECT membership_id FROM exit_requests WHERE approved IS NULL
            )
        """)
        return [dict(row) for row in cursor.fetchall()]

    def get_all_leaders(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.student_id, s.name as student_name, s.class, 
                   c.club_id, c.name as club_name, m.role
            FROM memberships m
            JOIN students s ON m.student_id = s.student_id
            JOIN clubs c ON m.club_id = c.club_id
            WHERE m.role IN ('Chairperson', 'Vice Chairperson', 'Secretary', 'Treasurer')
            AND m.is_active = 1
            ORDER BY c.name, m.role
        """)
        return [dict(row) for row in cursor.fetchall()]

    def update_club_leadership(self, club_id, **roles):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Reset all leadership roles first
            cursor.execute("""
                UPDATE memberships 
                SET role = 'Member'
                WHERE club_id = ? AND role IN (
                    'Chairperson', 'Vice Chairperson', 'Secretary', 'Treasurer'
                )
            """, (club_id,))
            
            # Update new leaders
            role_mapping = {
                'chairperson': 'Chairperson',
                'vice_chairperson': 'Vice Chairperson',
                'secretary': 'Secretary',
                'treasurer': 'Treasurer'
            }
            
            for field, role in role_mapping.items():
                student_id = roles.get(field)
                if student_id:
                    cursor.execute("""
                        UPDATE memberships 
                        SET role = ?
                        WHERE student_id = ? AND club_id = ?
                    """, (role, student_id, club_id))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            current_app.logger.error(f"Error updating leadership: {e}")
            raise

    def get_club_members(self, club_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.student_id, s.name, s.class, m.role, m.joined_date
            FROM memberships m
            JOIN students s ON m.student_id = s.student_id
            WHERE m.club_id = ? AND m.is_active = 1
            ORDER BY 
                CASE m.role
                    WHEN 'Chairperson' THEN 1
                    WHEN 'Vice Chairperson' THEN 2
                    WHEN 'Secretary' THEN 3
                    WHEN 'Treasurer' THEN 4
                    ELSE 5
                END, s.name
        """, (club_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_student_clubs(self, student_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.club_id, c.name, m.role, m.joined_date
            FROM memberships m
            JOIN clubs c ON m.club_id = c.club_id
            WHERE m.student_id = ? AND m.is_active = 1
            ORDER BY c.name
        """, (student_id,))
        return [dict(row) for row in cursor.fetchall()]