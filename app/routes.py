from app import app, db
from flask import render_template, redirect, url_for, request, flash
from app.forms import LoginForm, RegistrationForm, DishForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Dishes, Quantity
from werkzeug.urls import url_parse


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    dishes = Dishes.query.all()
    quantities = Quantity.query.filter_by(customer=current_user).all()
    form = DishForm()
    if form.validate_on_submit():
        dish = Dishes(dishname=form.dishname.data, amount=form.amount.data, timetaken=form.timetaken.data, quantity=0)
        db.session.add(dish)
        db.session.commit()
    return render_template('index.html', title='Home', dishes=dishes, form=form, quantities=quantities)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc!='':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/button/<dishname>', methods=['GET', 'POST'])
def button(dishname):
    if request.method == 'POST':
        dish = Dishes.query.filter_by(dishname=dishname).first()
        dishquantity = Quantity.query.filter_by(customer=current_user).filter_by(dish=dish).first()
        if dishquantity is None:
            dishquantity = Quantity(quantity=1, dish=dish, customer=current_user)
        else:
            dishquantity.quantity += 1
        db.session.commit()
    return redirect(url_for('index'))
