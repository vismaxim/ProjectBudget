from app import db, login_manager
from datetime import datetime, date
from flask_login import UserMixin
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False, unique=True)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Budgets(db.Model):
    __tablename__ = "Budgets"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    budgetname = db.Column(db.String(20), nullable=False)


class Transactions(db.Model):
    __tablename__ = "Transactions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    budget_id = db.Column(db.Integer, db.ForeignKey('Budgets.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    date = db.Column(db.DateTime, default=date.today())
    income = db.Column(db.Float, default=0)
    expense = db.Column(db.Float, default=0)
    balance = db.Column(db.Float)
    description = db.Column(db.String, db.ForeignKey('descript.id'))

    def __repr__(self):
        return "{}".format(self.id)

    def __init__(self, *args, **kwargs):
        super(Transactions, self).__init__(*args, **kwargs)


class Descriptions(db.Model):
    __tablename__ = 'descript'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20))

    def __repr__(self):
        return "{}".format(self.name)

    def __init__(self, *args, **kwargs):
        super(Descriptions, self).__init__(*args, **kwargs)


db.create_all()

