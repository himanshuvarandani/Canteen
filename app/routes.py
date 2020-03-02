from app import app, db
from flask import render_template, redirect, url_for, request, flash
from app.forms import LoginForm, RegistrationForm, DishForm, SearchForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Dishes, Quantity, History, Orders, RecentOrders
from werkzeug.urls import url_parse
from datetime import datetime
from datetime import timedelta
from config import Config


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    dishes = Dishes.query.all()
    quantities = Quantity.query.filter_by(customer=current_user).all()
    form = DishForm()
    form1 = SearchForm()
    if form.validate_on_submit():
        dish = Dishes(dishname=form.dishname.data, amount=form.amount.data, timetaken=form.timetaken.data, quantity=0)
        db.session.add(dish)
        users = User.query.all()
        for user in users:
            dishquantity = Quantity(quantity=0, dish=dish, customer=user)
            db.session.add(dishquantity)
        history = History(customer=current_user)
        db.session.add(history)
        order = Orders(history=history, quantity=0, dish=dish)
        db.session.add(order)
        db.session.commit()
    elif form1.validate_on_submit():
        return redirect(url_for('search', dishname=form1.search.data))
    return render_template('index.html', title='Home', dishes=dishes, form=form, quantities=quantities, form1=form1, next_page='index')


@app.route('/search/<dishname>', methods=["GET", "POST"])
def search(dishname):
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('search', dishname=form.search.data))
    dishes = Dishes.query.all()
    for dish in dishes:
        if dish.dishname.lower()==dishname.lower():
            quantity = Quantity.query.filter_by(customer=current_user).filter_by(dish=dish).first()
            return render_template('search.html', dish=dish, quantity=quantity, next_page='search', form=form)
    flash("Sorry, this dish is not available here.")
    return redirect(url_for('index'))


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


@app.route('/addbutton/<dishname>/<next_page>', methods=['GET', 'POST'])
def addbutton(dishname, next_page):
    if request.method == 'POST':
        dish = Dishes.query.filter_by(dishname=dishname).first()
        dishquantity = Quantity.query.filter_by(customer=current_user).filter_by(dish=dish).first()
        if dishquantity is None:
            dishquantity = Quantity(quantity=1, dish=dish, customer=current_user)
        else:
            dishquantity.quantity += 1
        db.session.commit()
    if next_page=='index':
        return redirect(url_for('index'))
    else:
        return redirect(url_for('search', dishname=dishname))


@app.route('/deletebutton/<dishname>/<next_page>', methods=['GET', 'POST'])
def deletebutton(dishname, next_page):
    if request.method == 'POST':
        dish = Dishes.query.filter_by(dishname=dishname).first()
        dishquantity = Quantity.query.filter_by(customer=current_user).filter_by(dish=dish).first()
        if dishquantity is None:
            dishquantity = Quantity(quantity=1, dish=dish, customer=current_user)
        else:
            if dishquantity.quantity>0:
                dishquantity.quantity -= 1
        db.session.commit()
    if next_page=='index':
        return redirect(url_for('index'))
    else:
        return redirect(url_for('search', dishname=dishname))


@app.route('/order', methods=['GET', 'POST'])
def order():
    t = app.config['T']
    print(t)
    if request.method == 'POST':
        dishes = Quantity.query.filter_by(customer=current_user).all()
        a = 0
        for dish in dishes:
            if dish.quantity!=0:
                if a==0:
                    flash("Your order is:")
                    recent_order = RecentOrders(customer=current_user, timestamp=datetime.utcnow())
                    history = History(customer=current_user, recent_order=recent_order)
                    db.session.add(recent_order)
                    db.session.add(history)
                    a = 1
                t += int(dish.dish.timetaken)*int(dish.quantity)
                order = Orders(history=history, quantity=dish.quantity, dish=dish.dish)
                db.session.add(order)
                flash("{} {}".format(dish.quantity, dish.dish.dishname))
                dish.quantity = 0
        if a==0:
            flash("Please select a dish.")
        else:
            recent_order.timestamp += timedelta(minutes=t)
            app.config['T'] = t
            db.session.commit()
    return redirect(url_for('index'))


@app.route('/remove/<dishname>', methods=['GET', 'POST'])
def remove(dishname):
    if request.method == 'POST':
        flash("You removed the dish {}".format(dishname))
        dish = Dishes.query.filter_by(dishname=dishname).first()
        quantities = Quantity.query.filter_by(dish=dish).all()
        for quantity in quantities:
            db.session.delete(quantity)
        db.session.delete(dish)
        db.session.commit()
    return redirect(url_for('index'))


@app.route('/history')
def history():
    histories = History.query.filter_by(customer=current_user).all()
    l = []
    t = app.config['T']
    for history in histories:
        if history.status == 0.5:
            recent_order = RecentOrders.query.filter_by(id=history.recent_order_id).first()
            if recent_order.timestamp<=datetime.utcnow():
                orders = Orders.query.filter_by(history=history).all()
                for dish in orders:
                    t -= int(dish.quantity)*int(dish.dish.timetaken)
                history.status = 1
                db.session.delete(recent_order)
                l.append((history, orders))
        else:
            orders = Orders.query.filter_by(history=history).all()
            l.append((history, orders))
    app.config['T'] = t
    db.session.commit()
    return render_template('history.html', l=l)


@app.route('/recent_orders', methods=['GET', 'POST'])
def recent_orders():
    recent_orders = RecentOrders.query.filter_by(customer=current_user).all()
    l = []
    t = app.config['T']
    for recent_order in recent_orders:
        history = History.query.filter_by(recent_order=recent_order).first()
        if recent_order.timestamp<=datetime.utcnow():
            orders = Orders.query.filter_by(history=history).all()
            for dish in orders:
                t -= int(dish.quantity)*int(dish.dish.timetaken)
            history.status = 1
            db.session.delete(recent_order)
        else:
            orders = Orders.query.filter_by(history=history).all()
            l.append((recent_order, history, orders))
    app.config['T'] = t
    db.session.commit()
    return render_template('recent_orders.html', l=l)


@app.route('/cancel/<order_id>', methods=['GET', 'POST'])
def cancel(order_id):
    recent_order = RecentOrders.query.filter_by(id=order_id).first()
    history = History.query.filter_by(recent_order=recent_order).first()
    t = app.config['T']
    orders = Orders.query.filter_by(history=history).all()
    for dish in orders:
        t -= int(dish.quantity)*int(dish.dish.timetaken)
    app.config['T'] = t
    history.status = 0
    db.session.delete(recent_order)
    db.session.commit()
    return redirect(url_for('recent_orders'))
