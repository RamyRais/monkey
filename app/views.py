from flask import render_template, redirect, url_for
from app import app, db
from app.forms import RegistrationForm, EditForm
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

@app.route('/profile/<name>/edit', methods=['GET', 'POST'])
def edit_profile(name=""):
    monkey = Monkey.query.filter_by(name=name).first()
    if monkey is None:
        return redirect(url_for('index'))
    form = EditForm()
    if form.validate_on_submit():
        number_errors = 0
        if monkey.email != form.email.data: #testing email unicity
            if Monkey.query.filter_by(email=form.email.data).first():
                form.email.errors.append("Email {0} is already used".format(
                    form.email.data))
                number_errors += 1
        if monkey.name != form.name.data: #testing name unicity
            if Monkey.query.filter_by(name=form.name.data).first():
                form.name.errors.append("Name {0} is already used".format(
                    form.name.data))
                number_errors += 1
        if number_errors > 0:
            return render_template('edit.html', form=form)       
        monkey.email = form.email.data
        monkey.name = form.name.data
        monkey.age = form.age.data
        db.session.add(monkey)
        db.session.commit()
        return redirect(url_for('profile', name=monkey.name))
    else:
        form.name.data = monkey.name
        form.email.data = monkey.email
        form.age.data = monkey.age
    return render_template('edit.html', form=form)