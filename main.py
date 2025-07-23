# Updated main.py
from data_access.student_dao import register_student
from data_access.membership_dao import join_club
from data_access.activity_dao import log_activity


def main():
    try:
        # Register new student
        student_id = register_student(
            admission_no="V2023012",
            name="David Kimani",
            class_="3W"
        )
        
        # Join clubs
        join_club(student_id=student_id, club_id=1)  # Debating Club
        join_club(student_id=student_id, club_id=3)  # Science Club
        
        # Log activity
        log_activity(
            club_id=1,  # Debating Club
            activity_name="Regional Debate Competition",
            activity_date="2024-04-20",
            revenue=8000
        )
        
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()