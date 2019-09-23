from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, SelectField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from models import Descriptions
from wtforms.fields.html5 import DateField
# from flask.ext.admin.form.widgets import DatePickerWidget


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

class NonValidateQuerySelectField(QuerySelectField):
    def pre_validate(self, form):
        return True

class BalanceForm(FlaskForm):
    income = FloatField('Income', default=0)
    expense = FloatField('Expense', default=0)
    # desc = Descriptions.query
    description = NonValidateQuerySelectField(query_factory=descript, allow_blank=True, get_label='name')
    submit = SubmitField('Apply')


class AnalyzeForm(FlaskForm):
    datestart = DateField('Choose date start', format='%Y-%m-%d')
    dateend = DateField('Choose date end', format='%Y-%m-%d')
    filtr = QuerySelectField(query_factory=descript, allow_blank=True, get_label='name')
    submit = SubmitField('Apply')
