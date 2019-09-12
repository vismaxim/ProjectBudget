from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, DateField, SelectField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from models import Descriptions


class RegistrationForm(FlaskForm):
    username = StringField('Login', validators=[DataRequired(), Length(min=2, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class AddUserForm(FlaskForm):
    username = StringField('Login', validators=[DataRequired(), Length(min=2, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Add User')


class CreateBudgetForm(FlaskForm):
    budgetname = StringField('Enter Budget Name')
    balance = FloatField('Enter initial balance')
    submit = SubmitField('Apply')


def descript():
    return Descriptions.query


class BalanceForm(FlaskForm):
    income = FloatField('Income', default=0)
    expense = FloatField('Expense', default=0)
    # desc = Descriptions.query
    description = QuerySelectField('Description', query_factory=descript, allow_blank=False, get_label='name')
    submit = SubmitField('Apply')


class AnalyzeForm(FlaskForm):
    datestart = DateField('Choose date start', format='%d/%m/%Y')
    dateend = DateField('Choose date end', format='%d/%m/%Y')
    # filtr = SelectField('Description')
    submit = SubmitField('Apply')
