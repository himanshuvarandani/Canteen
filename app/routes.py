from app import app
from flask import render_template, redirect, url_for
from app.forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
    dishes = [
        {'dishname':'a', 'count': 0},
        {'dishname':'b', 'count': 0},
        {'dishname':'c', 'count': 0},
        {'dishname':'d', 'count': 0},
        {'dishname':'e', 'count': 0}
        ]
    return render_template('index.html', title='Home', dishes=dishes)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Hello {}'.format(form.username.data))
        return redirect(url_for('index'))
    return render_template('/login.html', form=form, title='Sign In')
