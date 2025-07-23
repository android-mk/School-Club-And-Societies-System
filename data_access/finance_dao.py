from flask import current_app
from database.connection import get_db_connection

class FinanceDAO:
    def get_club_finances(self, club_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM finances 
            WHERE club_id = ?
            ORDER BY transaction_date DESC
        """, (club_id,))
        return [dict(row) for row in cursor.fetchall()]

    def record_fee_payment(self, club_id, amount):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO finances (club_id, amount, transaction_type, description, transaction_date)
                VALUES (?, ?, 'Registration Fee', 'Membership fee', date('now'))
            """, (club_id, amount))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            current_app.logger.error(f"Error recording fee payment: {e}")
            raise

    def get_financial_allocations(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN description LIKE '50%' THEN amount ELSE 0 END) as activities,
                SUM(CASE WHEN description LIKE '30%' THEN amount ELSE 0 END) as party,
                SUM(CASE WHEN description LIKE '20%' THEN amount ELSE 0 END) as savings,
                SUM(CASE WHEN transaction_type = 'School Contribution' THEN amount ELSE 0 END) as school_contribution
            FROM finances
        """)
        row = cursor.fetchone()
        return dict(row) if row else {
            'activities': 0,
            'party': 0,
            'savings': 0,
            'school_contribution': 0
        }

    def get_finances_by_club(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.name as club_name, 
                   SUM(f.amount) as total,
                   SUM(CASE WHEN f.transaction_type = 'Registration Fee' THEN f.amount ELSE 0 END) as fees,
                   SUM(CASE WHEN f.transaction_type = 'Revenue Allocation' THEN f.amount ELSE 0 END) as allocations,
                   SUM(CASE WHEN f.transaction_type = 'School Contribution' THEN f.amount ELSE 0 END) as school_contrib
            FROM finances f
            JOIN clubs c ON f.club_id = c.club_id
            GROUP BY c.club_id, c.name
        """)
        return [dict(row) for row in cursor.fetchall()]

    def get_financial_totals(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                SUM(amount) as grand_total,
                SUM(CASE WHEN transaction_type = 'Registration Fee' THEN amount ELSE 0 END) as total_fees,
                SUM(CASE WHEN transaction_type = 'Revenue Allocation' THEN amount ELSE 0 END) as total_allocations,
                SUM(CASE WHEN transaction_type = 'School Contribution' THEN amount ELSE 0 END) as total_school_contrib
            FROM finances
        """)
        row = cursor.fetchone()
        return dict(row) if row else {
            'grand_total': 0,
            'total_fees': 0,
            'total_allocations': 0,
            'total_school_contrib': 0
        }