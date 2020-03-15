from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from datetime import timedelta


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True, unique=True)
    email = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(32))
    dishes = db.relationship('Quantity', backref='customer', lazy='dynamic')
    history = db.relationship('History', backref='customer', lazy='dynamic')
    recent_orders = db.relationship('RecentOrders', backref='customer', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Dishes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dishname = db.Column(db.String(50), index=True, unique=True)
    amount = db.Column(db.Integer)
    timetaken = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    quantities = db.relationship('Quantity', backref='dish', lazy='dynamic')
    order = db.relationship('Orders', backref='dish', lazy='dynamic')

    def __repr__(self):
        return '{}: Price is {} and time taken is {}'.format(self.dishname, self.amount, self.timetaken)


class Quantity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer)
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=(datetime.now()-timedelta(minutes=330)))
    orders = db.relationship('Orders', backref='history', lazy='dynamic')
    status = db.Column(db.Integer, default=0.5)
    recent_order_id = db.Column(db.Integer, db.ForeignKey('recent_orders.id'))
    total_amount = db.Column(db.Integer, default = 0)

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    history_id = db.Column(db.Integer, db.ForeignKey('history.id'))
    quantity = db.Column(db.Integer)
    dish_id = db.Column(db.Integer, db.ForeignKey('dishes.id'))


class RecentOrders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    history = db.relationship('History', backref='recent_order', lazy='dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
