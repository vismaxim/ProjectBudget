import os
import secrets
from app import app, db, bcrypt
from flask import render_template, flash, url_for, redirect, request
from forms import RegistrationForm, LoginForm, BalanceForm, CreateBudgetForm, AnalyzeForm, UpdateAccountForm
from datetime import timedelta, datetime, date
from flask_login import login_user, current_user, logout_user, login_required
from models import Users, Transactions, Budgets, Descriptions
from PIL import Image


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
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/budgets")
def budgets():
    budgets = Budgets.query.filter_by(user_id=current_user.id)
    budgetsname = db.session.query(Budgets.budgetname).filter_by(user_id=current_user.id)

    return render_template('budgets.html', budgets=budgets, budgetsname=budgetsname)


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
        d1 = form.descriptions.data
        d = d1.split(' ')
        for name in d:
            desc = Descriptions(budget_id=budget_id, name=name)
            db.session.add(desc)
        db.session.commit()
        flash(f'Budget {form.budgetname.data} created')
        return redirect(url_for('budgets'))
    return render_template('create_budget.html', title='create_budget', form=form)


@app.route("/budget/<int:budget_id>/delete", methods=['POST'])
@login_required
def del_budget(budget_id):
    bud = Budgets.query.get(budget_id)
    db.session.query(Transactions).filter_by(budget_id=budget_id).delete()
    db.session.query(Descriptions).filter_by(budget_id=budget_id).delete()
    db.session.delete(bud)
    db.session.commit()
    flash('Your budget has been deleted!', 'success')
    return redirect(url_for('budgets'))


@app.route("/budget/<int:budget_id>", methods=['GET', "POST"])
@login_required
def budget(budget_id):
    b = Budgets.query.get(budget_id)
    transact = Transactions.query.filter_by(budget_id=budget_id)[-1]

    form = BalanceForm()

    form.description.query = Descriptions.query.filter_by(budget_id=budget_id)

    if form.validate_on_submit():
        if form.income.data == 0 and form.expense.data == 0:
            flash('Insert, at least, income or expense')
            return redirect(url_for('budget', budget_id=budget_id))
        # if form.description.data == None:
        #     flash('Choose description')
        #     return redirect(url_for('budget', budget_id=budget_id))
        tr = transact.balance - form.expense.data
        tr = tr + form.income.data

        transaction = Transactions(budget_id=budget_id, income=form.income.data, expense=form.expense.data,
                             user_id=current_user.id, balance=tr, description=(None if form.description.data == None else form.description.data.name))

        db.session.add(transaction)
        db.session.commit()
        return redirect(url_for('budget', budget_id=budget_id))
    return render_template('budget.html', title='enter data', budget=b, bal=transact, form=form)


@app.route("/budget/<int:budget_id>/analyze", methods=['GET', "POST"])
@login_required
def analyze_bud(budget_id):
    b = Budgets.query.get(budget_id)
    form = AnalyzeForm()
    form.filtr.query = Descriptions.query.filter_by(budget_id=budget_id)
    transact = Transactions.query.filter_by(budget_id=budget_id)[-1]

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
            items = db.session.query(str(Transactions.date), Transactions.income, Transactions.expense,
                                     Transactions.balance, Transactions.description).filter(
                Transactions.budget_id == budget_id).filter(
                Transactions.date >= form.datestart.data).filter(Transactions.date < (
                    form.dateend.data + one_day)).filter(Transactions.description == str(form.filtr.data)).all()
        else:
            income = db.session.query(db.func.sum(Transactions.income)). filter(
                Transactions.budget_id == budget_id).filter(
                Transactions.date >= form.datestart.data).filter(
                Transactions.date < (form.dateend.data + one_day)).scalar()
            expense = db.session.query(db.func.sum(Transactions.expense)). filter(
                Transactions.budget_id == budget_id).filter(
                Transactions.date >= form.datestart.data).filter(
                Transactions.date < (form.dateend.data + one_day)).scalar()

            items = db.session.query(str(Transactions.date), Transactions.income, Transactions.expense, Transactions.balance, Transactions.description). filter(
                Transactions.budget_id == budget_id).filter(
                Transactions.date >= form.datestart.data).filter(Transactions.date < (
                    form.dateend.data + one_day)).all()

        return render_template('analyze_bud.html', title='Analyze Budget', budget=b, bal=transact, form=form, income=income, expense=expense, items=items)
    return render_template('analyze_bud.html', title='Analyze Budget', budget=b, bal=transact, form=form)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + str(current_user.image_file))
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)