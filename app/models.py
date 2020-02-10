from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True, unique=True)
    email = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(32))

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

    def __repr__(self):
        return '{}: Price is {} and time taken is {}'.format(self.dishname, self.amount, self.timetaken)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
