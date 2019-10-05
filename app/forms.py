from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, SelectField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import Users, Descriptions
from wtforms.fields.html5 import DateField
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed


class RegistrationForm(FlaskForm):
    username = StringField('Login', validators=[DataRequired(), Length(min=2, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign up')

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class CreateBudgetForm(FlaskForm):
    budgetname = StringField('Enter Budget Name')
    balance = FloatField('Enter initial balance')
    submit = SubmitField('Apply')


def descript():
    return Descriptions.query


class NonValidateQuerySelectField(QuerySelectField):
    def pre_validate(self, form):
        return True


class BalanceForm(FlaskForm):
    income = FloatField('Income', default=0)
    expense = FloatField('Expense', default=0)
    description = NonValidateQuerySelectField(query_factory=descript, allow_blank=True, get_label='name')
    submit = SubmitField('Apply')


class AnalyzeForm(FlaskForm):
    datestart = DateField('Choose date from', format='%Y-%m-%d')
    dateend = DateField('Choose date to', format='%Y-%m-%d')
    filtr = QuerySelectField(query_factory=descript, allow_blank=True, get_label='name')
    submit = SubmitField('Apply')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = Users.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = Users.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')