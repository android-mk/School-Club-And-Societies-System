from flask import current_app
from database.connection import get_db_connection

class StudentDAO:
    def get_all_students(self):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            current_app.logger.error(f"Error getting all students: {e}")
            raise

    def get_student_choices(self):
        try:
            students = self.get_all_students()
            return [(s['student_id'], f"{s['name']} ({s['class']})") for s in students]
        except Exception as e:
            current_app.logger.error(f"Error getting student choices: {e}")
            raise

    def get_student_with_clubs(self, student_id):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
            row = cursor.fetchone()
            student = dict(row) if row else None
            
            if student:
                cursor.execute("""
                    SELECT c.club_id, c.name, m.role, m.joined_date, m.is_active
                    FROM memberships m
                    JOIN clubs c ON m.club_id = c.club_id
                    WHERE m.student_id = ?
                    ORDER BY m.is_active DESC, c.name
                """, (student_id,))
                student['clubs'] = [dict(row) for row in cursor.fetchall()]
            
            return student
        except Exception as e:
            current_app.logger.error(f"Error getting student with clubs: {e}")
            raise

    def register_student_with_club(self, admission_no, name, class_, club_id, role):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO students (admission_no, name, class) VALUES (?, ?, ?)",
                (admission_no, name, class_)
            )
            student_id = cursor.lastrowid
            
            cursor.execute("""
                INSERT INTO memberships (student_id, club_id, role, joined_date, is_active)
                VALUES (?, ?, ?, date('now'), 1)
            """, (student_id, club_id, role))
            
            conn.commit()
            return student_id
        except Exception as e:
            conn.rollback()
            current_app.logger.error(f"Error registering student: {e}")
            raise