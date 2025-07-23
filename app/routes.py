from flask import render_template, redirect, url_for, flash, request
from app.forms import (
    StudentRegistrationForm, ClubActivityForm, 
    MembershipForm, ExitRequestForm, PatronForm 
)
from data_access.student_dao import StudentDAO
from data_access.club_dao import ClubDAO
from data_access.membership_dao import MembershipDAO
from data_access.finance_dao import FinanceDAO
from data_access.activity_dao import ActivityDAO
from data_access.patron_dao import PatronDAO
from database.connection import get_db_connection

# Initialize DAOs
student_dao = StudentDAO()
club_dao = ClubDAO()
membership_dao = MembershipDAO()
finance_dao = FinanceDAO()
activity_dao = ActivityDAO()
patron_dao = PatronDAO()

def init_app(app):
    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register_student_route():
        form = StudentRegistrationForm()
        form.club_id.choices = club_dao.get_club_choices()
        
        if form.validate_on_submit():
            try:
                student_dao.register_student_with_club(
                    admission_no=form.admission_no.data,
                    name=form.name.data,
                    class_=form.class_.data,
                    club_id=form.club_id.data,
                    role=form.role.data
                )
                flash('Student registered and club membership created!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')
        
        return render_template('register.html', form=form)

    @app.route('/join_club', methods=['GET', 'POST'])
    def join_club():
        club_id = request.args.get('club_id')
        form = MembershipForm()
        
        form.student_id.choices = student_dao.get_student_choices()
        form.club_id.choices = club_dao.get_club_choices()
        
        if club_id:
            form.club_id.data = int(club_id)
        
        if form.validate_on_submit():
            try:
                if membership_dao.is_student_in_club(form.student_id.data, form.club_id.data):
                    flash('Student is already a member of this club!', 'warning')
                    return redirect(url_for('join_club'))
                
                fee_amount = club_dao.get_club_fee(form.club_id.data)
                membership_dao.create_membership(
                    form.student_id.data,
                    form.club_id.data,
                    form.role.data
                )
                finance_dao.record_fee_payment(form.club_id.data, fee_amount)
                
                flash('Student successfully joined the club!', 'success')
                return redirect(url_for('club_details', club_id=form.club_id.data))
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')
        
        return render_template('join_club.html', form=form)

    @app.route('/exit_request/<int:membership_id>', methods=['GET', 'POST'])
    def exit_request(membership_id):
        membership = membership_dao.get_membership(membership_id)
        form = ExitRequestForm()
        
        if membership['role'] == 'Member':
            try:
                membership_dao.deactivate_membership(membership_id)
                flash('Membership deactivated', 'success')
                return redirect(url_for('dashboard'))
            except ValueError as e:
                flash(str(e), 'danger')
                return redirect(url_for('dashboard'))
        
        if form.validate_on_submit():
            try:
                if form.approved.data:
                    membership_dao.deactivate_membership(membership_id)
                    membership_dao.log_approval(membership_id, form.approval_notes.data)
                    flash('Exit approved and membership deactivated', 'success')
                else:
                    flash('Exit request denied', 'warning')
                return redirect(url_for('dashboard'))
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')
        
        return render_template('exit_request.html', form=form, membership=membership)

    @app.route('/manage_clubs')
    def manage_clubs():
        clubs = club_dao.get_all_clubs_with_stats()
        return render_template('manage_clubs.html', clubs=clubs)

    @app.route('/club_details/<int:club_id>')
    def club_details(club_id):
        club = club_dao.get_club_with_details(club_id)
        finances = finance_dao.get_club_finances(club_id)
        return render_template('club_details.html', 
                            club=club, 
                            finances=finances, 
                            all_patrons=patron_dao.get_all_patrons())

    @app.route('/student_details/<int:student_id>')
    def student_details(student_id):
        student = student_dao.get_student_with_clubs(student_id)
        return render_template('student_details.html', student=student)

    @app.route('/add_patron', methods=['GET', 'POST'])
    def add_patron():
        form = PatronForm()
        if form.validate_on_submit():
            try:
                patron_dao.add_patron(form.name.data, form.email.data)
                flash('Patron added successfully!', 'success')
                return redirect(url_for('manage_clubs'))
            except Exception as e:
                flash(f'Error adding patron: {str(e)}', 'danger')
        return render_template('add_patron.html', form=form)

    @app.route('/assign_leadership', methods=['POST'])
    def assign_leadership():
        if request.method == 'POST':
            club_id = request.form.get('club_id')
            
            try:
                membership_dao.update_club_leadership(
                    club_id,
                    chairperson=request.form.get('chairperson'),
                    vice_chairperson=request.form.get('vice_chairperson'),
                    secretary=request.form.get('secretary'),
                    treasurer=request.form.get('treasurer')
                )
                flash('Leadership roles updated successfully!', 'success')
            except Exception as e:
                flash(f'Error updating roles: {str(e)}', 'danger')
                app.logger.error(f"Error in assign_leadership: {str(e)}")
            
            return redirect(url_for('club_details', club_id=club_id))

    @app.route('/assign_patron', methods=['POST'])
    def assign_patron():
        if request.method == 'POST':
            club_id = request.form.get('club_id')
            patron_id = request.form.get('patron_id')
            
            if not patron_id:
                flash('Please select a patron', 'danger')
                return redirect(url_for('club_details', club_id=club_id))
            
            try:
                club_dao.assign_patron(club_id, patron_id)
                flash('Patron assigned successfully!', 'success')
            except Exception as e:
                flash(f'Error assigning patron: {str(e)}', 'danger')
            
            return redirect(url_for('club_details', club_id=club_id))

    @app.route('/dashboard')
    def dashboard():
        activities = activity_dao.get_recent_activities(limit=5)
        pending_approvals = membership_dao.get_pending_approvals()
        allocations = finance_dao.get_financial_allocations()
        clubs = club_dao.get_clubs_summary()
        totals = finance_dao.get_financial_totals()
        return render_template('dashboard.html', 
                            activities=activities,
                            pending_approvals=pending_approvals,
                            allocations=allocations,
                            clubs=clubs,
                            totals=totals)

    @app.route('/log_activity', methods=['GET', 'POST'])
    def log_activity():
        form = ClubActivityForm()
        form.club_id.choices = club_dao.get_club_choices()
        
        if form.validate_on_submit():
            try:
                revenue = float(form.revenue.data)
                allocations = {
                    'activities': revenue * 0.5,
                    'party': revenue * 0.3,
                    'savings': revenue * 0.2
                }
                school_contribution = allocations['party'] * 0.7
                
                activity_dao.log_activity_with_allocations(
                    club_id=form.club_id.data,
                    activity_name=form.activity_name.data,
                    activity_date=form.activity_date.data,
                    revenue=revenue,
                    allocations=allocations,
                    school_contribution=school_contribution
                )
                flash('Activity logged with allocations!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                flash(f'Error: {str(e)}', 'danger')
        
        return render_template('log_activity.html', form=form)

    @app.route('/all_patrons')
    def all_patrons():
        patrons = patron_dao.get_all_patrons()
        clubs = club_dao.get_all_clubs()  
        return render_template('all_patrons.html', patrons=patrons, clubs=clubs)

    @app.route('/all_leaders')
    def all_leaders():
        leaders = membership_dao.get_all_leaders()
        return render_template('club_leaders.html', leaders=leaders)

    @app.route('/all_students')
    def all_students():
        students = student_dao.get_all_students()
        return render_template('students.html', students=students)

    @app.route('/all_activities')
    def all_activities():
        activities = activity_dao.get_all_activities()
        return render_template('activities.html', activities=activities)

    @app.route('/financial_summary')
    def financial_summary():
        club_finances = finance_dao.get_finances_by_club()
        totals = finance_dao.get_financial_totals()
        allocations = finance_dao.get_financial_allocations()
        
        return render_template('finance.html', 
                            club_finances=club_finances,
                            totals=totals,
                            allocations=allocations)

    @app.route('/club_activities/<int:club_id>')
    def club_activities(club_id):
        club = club_dao.get_club(club_id)
        if not club:
            flash('Club not found', 'danger')
            return redirect(url_for('dashboard'))
        
        past_activities = activity_dao.get_past_activities(club_id)
        upcoming_activities = activity_dao.get_upcoming_activities(club_id)
        
        return render_template('club_activities.html', 
                            club=club,
                            past_activities=past_activities,
                            upcoming_activities=upcoming_activities)

    @app.route('/search_student')
    def search_student():
        return render_template('search_student.html')

    @app.route('/exit_club')
    def exit_club():
        return render_template('exit_club.html')