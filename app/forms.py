from app.models import User, Dishes
from flask_wtf import FlaskForm
from flask import request, url_for
from wtforms import BooleanField, IntegerField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=15)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please Use a different username')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please Use a different email address')


class DishForm(FlaskForm):
    dishname = StringField('Dish Name', validators=[DataRequired()])
    amount = IntegerField('Amount', validators=[DataRequired()])
    timetaken = IntegerField('Time taken(in minutes)', validators=[DataRequired()])
    submit = SubmitField('Add')

    def validate_dishname(self, dishname):
        dish = Dishes.query.filter_by(dishname=dishname.data.upper()).first()
        if dish is not None:
            if url_for('modify', dishname=dish.dishname) not in request.base_url:
                raise ValidationError('This dish is already exist.')


class SearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')
