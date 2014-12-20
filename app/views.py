from flask import render_template, redirect, url_for
from app import app, db
from app.forms import RegistrationForm
from app.models import Monkey
from config import MONKEYS_PER_PAGE

@app.route('/')
@app.route('/index')
@app.route('/index/<int:page>')
def index(page=1):
    monkeys = Monkey.query.paginate(page, MONKEYS_PER_PAGE, False)
    return render_template("index.html", title='home', monkeys=monkeys)

@app.route('/addmonkey', methods=['GET', 'POST'])
def add_monkey():
    form = RegistrationForm()
    if form.validate_on_submit():
        monkey = Monkey()
        form.populate_obj(monkey)
        db.session.add(monkey)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('addMonkey.html', title='Add Monkey', form=form)

@app.route('/profile/<name>')
def profile(name=""):
    monkey = Monkey.query.filter_by(name=name).first()
    if monkey is None:
        return redirect(url_for('index'))
    return render_template('profile.html', monkey=monkey,
                           title='{0} profile'.format(monkey.name))
