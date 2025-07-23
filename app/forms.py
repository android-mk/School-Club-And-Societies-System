from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, DateField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email

class StudentRegistrationForm(FlaskForm):
    admission_no = StringField('Admission Number', validators=[DataRequired()])
    name = StringField('Full Name', validators=[DataRequired()])
    class_ = StringField('Class (e.g., 3E)', validators=[DataRequired()])
    club_id = SelectField('Primary Club', coerce=int, validators=[DataRequired()])
    role = SelectField('Initial Role', choices=[
        ('Member', 'Member'),
        ('Chairperson', 'Chairperson'),
        ('Vice Chairperson', 'Vice Chairperson'),
        ('Secretary', 'Secretary'),
        ('Treasurer', 'Treasurer')
    ], default='Member')

class ClubActivityForm(FlaskForm):
    club_id = SelectField('Club', coerce=int, validators=[DataRequired()])
    activity_name = StringField('Activity Name', validators=[DataRequired()])
    activity_date = DateField('Date', validators=[DataRequired()])
    revenue = DecimalField('Revenue Generated', validators=[DataRequired()])

class ClubForm(FlaskForm):
    name = StringField('Club Name', validators=[DataRequired()])
    fee_amount = DecimalField('Registration Fee', validators=[DataRequired()])
    patron_id = SelectField('Patron', coerce=int, validators=[DataRequired()])

class PatronForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Save Patron')
class MembershipForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    club_id = SelectField('Club', coerce=int, validators=[DataRequired()])
    role = SelectField('Role', choices=[
        ('Member', 'Member'),
        ('Chairperson', 'Chairperson'),
        ('Vice Chairperson', 'Vice Chairperson'),
        ('Secretary', 'Secretary'),
        ('Treasurer', 'Treasurer')
    ])
    is_active = BooleanField('Active Membership', default=True)

class ExitRequestForm(FlaskForm):
    approval_notes = StringField('Patron Approval Notes')
    approved = BooleanField('Approved')