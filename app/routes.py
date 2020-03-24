import time

from app import app, db, mail
from app.forms import DishForm, LoginForm, RegistrationForm, SearchForm
from app.models import Dishes, History, Orders, Quantity, RecentOrders, User
from config import Config
from datetime import datetime
from datetime import timedelta
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message
from threading import Thread
from werkzeug.urls import url_parse


def notification(app, wait_time, user_email):
    time.sleep((wait_time-1)*60)
    with app.app_context():
        msg = Message('Order Completion', sender=app.config['ADMINS'][0], recipients=[user_email])
        msg.body = 'Your order is completed.'
        msg.html = '<h1>Order Completion</h1>'
        mail.send(msg)


def time_correction():
    wait_time, t = app.config['WAIT_TIME'], 0

    recent_orders = RecentOrders.query.all()
    for recent_order in recent_orders:
        history = History.query.filter_by(recent_order=recent_order).first()
        if recent_order.timestamp+timedelta(minutes=330) <= datetime.now():
            orders = Orders.query.filter_by(history=history).all()
            for dish in orders:
                wait_time -= int(dish.quantity)*int(dish.dish.timetaken)
            history.status = 1
            db.session.delete(recent_order)
    
    app.config['WAIT_TIME'] = wait_time
    db.session.commit()

    if recent_orders:
        print(datetime.now(), recent_order.timestamp+timedelta(minutes=330))
        t = (recent_order.timestamp+timedelta(minutes=330)-datetime.now()).total_seconds()
        print(t//60+1)
        return (t//60+1)
    return 0


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    t = time_correction()
    if current_user.username != "admin":
        if t == 0:
            flash('Your order will be accepted fast.')
        else:
            flash('Your order will be accepted after {} minutes'.format(t))

    dishes = Dishes.query.all()
    quantities = Quantity.query.filter_by(customer=current_user).all()
    form = DishForm()
    form1 = SearchForm()

    if form.validate_on_submit():
        dish = Dishes(dishname=form.dishname.data, amount=form.amount.data,
            timetaken=form.timetaken.data, quantity=0)
        db.session.add(dish)
        users = User.query.all()
        for user in users:
            dishquantity = Quantity(quantity=0, dish=dish, customer=user)
            db.session.add(dishquantity)
        history = History(customer=current_user,
            timestamp=(datetime.now()-timedelta(minutes=330)),
            status=1)
        db.session.add(history)
        order = Orders(history=history, quantity=0, dish=dish)
        db.session.add(order)
        db.session.commit()
        flash('You add the dish {}'.format(dish.dishname))
    elif form1.validate_on_submit():
        return redirect(url_for('search', dishname=form1.search.data))

    return render_template('index.html', title='Home',
        dishes=dishes, form=form, quantities=quantities,
        form1=form1, next_page='index')


@app.route('/search/<dishname>', methods=["GET", "POST"])
@login_required
def search(dishname):
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('search', dishname=form.search.data))

    dishes = Dishes.query.all()
    for dish in dishes:
        if dish.dishname.lower()==dishname.lower():
            quantity = Quantity.query.filter_by(customer=current_user) \
                .filter_by(dish=dish).first()
            return render_template('search.html', title='Search',
                dish=dish, quantity=quantity,
                next_page='search', form=form)

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
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)

        dishes = Dishes.query.all()
        for dish in dishes:
            dishquantity = Quantity(quantity=0, dish=dish, customer=user)
            db.session.add(dishquantity)
        db.session.commit()

        flash('Congratulations, you are registered user!')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)


@app.route('/addbutton/<dishname>/<next_page>', methods=['GET', 'POST'])
@login_required
def addbutton(dishname, next_page):
    if request.method == 'POST':
        dish = Dishes.query.filter_by(dishname=dishname).first()
        dishquantity = Quantity.query.filter_by(customer=current_user) \
            .filter_by(dish=dish).first()
        if dishquantity is None:
            dishquantity = Quantity(quantity=1, dish=dish,
                customer=current_user)
        else:
            dishquantity.quantity += 1
        db.session.commit()

    if next_page=='index':
        return redirect(url_for('index'))
    else:
        return redirect(url_for('search', dishname=dishname))


@app.route('/deletebutton/<dishname>/<next_page>', methods=['GET', 'POST'])
@login_required
def deletebutton(dishname, next_page):
    if request.method == 'POST':
        dish = Dishes.query.filter_by(dishname=dishname).first()
        dishquantity = Quantity.query.filter_by(customer=current_user) \
            .filter_by(dish=dish).first()
        if dishquantity is None:
            dishquantity = Quantity(quantity=1, dish=dish,
                customer=current_user)
        else:
            if dishquantity.quantity>0:
                dishquantity.quantity -= 1
        db.session.commit()

    if next_page=='index':
        return redirect(url_for('index'))
    else:
        return redirect(url_for('search', dishname=dishname))


@app.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    flag, total_amount, time_taken = 0, 0, 0
    t = time_correction()
    if request.method == 'POST':
        dishes = Quantity.query.filter_by(customer=current_user).all()
        for dish in dishes:
            if dish.quantity!=0:
                if flag==0:
                    flash("Your order is:")
                    recent_order = RecentOrders(customer=current_user,
                        timestamp=(datetime.now()-timedelta(minutes=330)))
                    history = History(customer=current_user,
                        timestamp=(datetime.now()-timedelta(minutes=330)),
                        recent_order=recent_order)
                    db.session.add(recent_order)
                    db.session.add(history)
                    flag = 1
                time_taken += int(dish.dish.timetaken)*int(dish.quantity)
                total_amount += int(dish.dish.amount)*int(dish.quantity)
                order = Orders(history=history,
                    quantity=dish.quantity,
                    dish=dish.dish)
                db.session.add(order)
                flash("{} {} {}".format(dish.quantity,
                    dish.dish.dishname,
                    dish.quantity*dish.dish.amount))
                dish.quantity = 0

        if flag==0:
            flash("Please select a dish.")
        else:
            user_email = current_user.email
            Thread(target=notification,
                args=(app, t+time_taken, user_email)).start()

            recent_order.timestamp += timedelta(minutes=(t+time_taken))
            history.total_amount = total_amount
            app.config['WAIT_TIME'] += time_taken
            db.session.commit()
    return redirect(url_for('index'))


@app.route('/remove/<dishname>', methods=['GET', 'POST'])
@login_required
def remove(dishname):
    if request.method == 'POST':
        flash("You removed the dish {}".format(dishname))
        dish = Dishes.query.filter_by(dishname=dishname).first()
        quantities = Quantity.query.filter_by(dish=dish).all()
        for quantity in quantities:
            db.session.delete(quantity)
        history = History(customer=current_user,
            timestamp=(datetime.now()-timedelta(minutes=330)),
            status=0, removed_dish=dish.dishname)
        db.session.add(history)
        db.session.delete(dish)
        db.session.commit()
    return redirect(url_for('index'))


@app.route('/history/<start>')
@login_required
def history(start):
    L, t = [], time_correction()
    histories = History.query.filter_by(customer=current_user).all()
    for history in histories:
        if history.status != 0.5:
            orders = Orders.query.filter_by(history=history).all()
            L.append((history, orders))

    if not L:
        if current_user.username == 'admin':
            flash("You do not add any dish")
        else:
            flash("You do not order anything till now.")
        return redirect(url_for('index'))

    total = len(L)
    start = int(start)
    if start>total:
        return render_template('404.html') or 404

    if start+10<total:
        end = start+10
    else:
        end = total+1
    return render_template('history.html', title='History', L=L,
        start=start, end=end, total=total)


@app.route('/recent_orders', methods=['GET', 'POST'])
@login_required
def recent_orders():
    L, t = [], time_correction()

    recent_orders = RecentOrders.query.filter_by(customer=current_user).all()
    for recent_order in recent_orders:
        history = History.query.filter_by(recent_order=recent_order).first()
        orders = Orders.query.filter_by(history=history).all()
        L.append((recent_order, history, orders))
    
    if not L:
        flash("You do not order anything till now or your orders are \
            completed or cancelled.")
        flash("See the status in history.")
        return redirect(url_for('index'))

    return render_template('recent_orders.html', title='Recent Orders', L=L)


@app.route('/cancel/<order_id>', methods=['GET', 'POST'])
@login_required
def cancel(order_id):
    wait_time = app.config['WAIT_TIME']

    recent_order = RecentOrders.query.filter_by(id=order_id).first()
    history = History.query.filter_by(recent_order=recent_order).first()
    flash('Your order at {} is cancelled'.format(history.timestamp))
    flash('Details:')

    orders = Orders.query.filter_by(history=history).all()
    for dish in orders:
        flash("{} {} {}".format(dish.quantity,
            dish.dish.dishname,
            dish.dish.amount))
        wait_time -= int(dish.quantity)*int(dish.dish.timetaken)
    flash('Total cost: {}'.format(history.total_amount))
    app.config['WAIT_TIME'] = wait_time
    history.status = 0
    db.session.delete(recent_order)
    db.session.commit()
    return redirect(url_for('index'))
