import os
from app import app, db, bcrypt
from flask import render_template, flash, url_for, redirect, request
from forms import RegistrationForm, LoginForm, AddUserForm, BalanceForm, CreateBudgetForm, AnalyzeForm
from datetime import timedelta, datetime, date
from flask_login import login_user, current_user, logout_user, login_required
from models import Users, Transactions, Budgets, Descriptions


@app.route("/")
@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Users(username=form.username.data, email=form.email.data, password=hash_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/signin", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('budgets'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('budgets'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


# @app.route("/<str:current_user.username>")
# @login_required
# def user(current_user):
#     b = Budgets.query.get(current_user)
#     return render_template('user.html', title=b.title, b=b)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/budgets")
def budgets():
    budgets = Budgets.query.filter_by(user_id=current_user.id)
    return render_template('budgets.html', budgets=budgets)


@app.route("/create_budget", methods=['GET', 'POST'])
@login_required
def create_budget():
    form = CreateBudgetForm()
    if form.validate_on_submit():
        budget = Budgets(budgetname=form.budgetname.data, user_id=current_user.id)
        db.session.add(budget)
        db.session.commit()
        budget_id = db.session.query(Budgets.id).order_by(Budgets.id.desc())
        transact = Transactions(budget_id=budget_id, user_id=current_user.id, balance=form.balance.data)

        db.session.add(transact)
        db.session.commit()
        flash(f'Budget {form.budgetname.data} created')
        return redirect(url_for('budgets'))
    return render_template('create_budget.html', title='create_budget', form=form)


@app.route("/budget/<int:budget_id>/delete", methods=['POST'])
@login_required
def del_budget(budget_id):
    bud = Budgets.query.get(budget_id)
    db.session.query(Transactions).filter_by(budget_id=budget_id).delete()
    db.session.delete(bud)
    db.session.commit()
    flash('Your budget has been deleted!', 'success')
    return redirect(url_for('budgets'))


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title='Account')


@app.route("/budget/<int:budget_id>", methods=['GET', "POST"])
@login_required
def budget(budget_id):
    b = Budgets.query.get(budget_id)
    transact = Transactions.query.filter_by(budget_id=budget_id)[-1]
    # desc = Descriptions.query.get
    form = BalanceForm()
    # form.description.choices = [(description.id, description.name) for description in Descriptions.query.all()]

    if form.validate_on_submit():
        if form.income.data == 0 and form.expense.data == 0:
            flash('Insert, at least, income or expense')
            return redirect(url_for('budget'))
        tr = transact.balance - form.expense.data
        tr = tr + form.income.data

        transaction = Transactions(budget_id=budget_id, income=form.income.data, expense=form.expense.data,
                             user_id=current_user.id, balance=tr, description=form.description.data.name)

        db.session.add(transaction)
        db.session.commit()
        return redirect(url_for('budget', budget_id=budget_id))
    return render_template('budget.html', title='enter data', budget=b, bal=transact, form=form)


@app.route("/budget/<int:budget_id>/analyze", methods=['GET', "POST"])
@login_required
def analyze_bud(budget_id):
    b = Budgets.query.get(budget_id)
    form = AnalyzeForm()
    # form.filtr.choices = [(filtr.id, filtr.name) for filtr in Descriptions.query.all()]
    transact = Transactions.query.filter_by(budget_id=budget_id)[-1]
    # desc = Descriptions.query.get

    if form.validate_on_submit():
        one_day = timedelta(1)

        if form.filtr.data != None:

            income = db.session.query(db.func.sum(Transactions.income)). filter(
                Transactions.budget_id == budget_id).filter(
                Transactions.date >= form.datestart.data).filter(Transactions.date < (
                    form.dateend.data + one_day)).filter(Transactions.description == str(form.filtr.data)).scalar()
            expense = db.session.query(db.func.sum(Transactions.expense)). filter(
                Transactions.budget_id == budget_id).filter(
                Transactions.date >= form.datestart.data).filter(Transactions.date < (
                    form.dateend.data + one_day)).filter(Transactions.description == str(form.filtr.data)).scalar()
        else:
            income = db.session.query(db.func.sum(Transactions.income)). filter(
                Transactions.budget_id == budget_id).filter(
                Transactions.date >= form.datestart.data).filter(
                Transactions.date < (form.dateend.data + one_day)).scalar()
            expense = db.session.query(db.func.sum(Transactions.expense)). filter(
                Transactions.budget_id == budget_id).filter(
                Transactions.date >= form.datestart.data).filter(
                Transactions.date < (form.dateend.data + one_day)).scalar()


        return render_template('analyze_bud.html', title='Analyze Budget', budget=b, bal=transact, form=form, income=income, expense=expense)
    return render_template('analyze_bud.html', title='Analyze Budget', budget=b, bal=transact, form=form)


@app.route("/adduser", methods=['GET', 'POST'])
def add_user():
    add_user = Users.query
    return render_template('adduser.html', title='Add User', users=add_user)