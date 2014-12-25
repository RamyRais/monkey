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

@app.route('/profile/<name>/relations')
def show_relations(name=""):
    monkey = Monkey.query.filter_by(name=name).first()
    if monkey is None:
        return redirect(url_for('index'))
    friends = monkey.friends
    not_friends = monkey.not_friends()
    return render_template('relation.html', monkey=monkey,
                           friends=friends, notFriends=not_friends)

@app.route('/removefriend/<monkey_name>/<friend_name>')
def removefriend(monkey_name, friend_name):
    monkey = Monkey.query.filter_by(name=monkey_name).first()
    friend = Monkey.query.filter_by(name=friend_name).first()
    monkey.remove_friend(friend)
    db.session.add(monkey)
    db.session.add(friend)
    db.session.commit()
    return redirect(url_for('show_relations', name=monkey_name))

@app.route('/addfriend/<monkey_name>/<friend_name>')
def addfriend(monkey_name, friend_name):
    monkey = Monkey.query.filter_by(name=monkey_name).first()
    friend = Monkey.query.filter_by(name=friend_name).first()
    monkey.add_friend(friend)
    db.session.add(monkey)
    db.session.add(friend)
    db.session.commit()
    return redirect(url_for('show_relations', name=monkey_name))

@app.route('/makebestfriend/<monkey_name>/<friend_name>')
def add_best_friend(monkey_name, friend_name):
    monkey = Monkey.query.filter_by(name=monkey_name).first()
    friend = Monkey.query.filter_by(name=friend_name).first()
    monkey.make_best_friend(friend)
    db.session.add(monkey)
    db.session.commit()
    return redirect(url_for('show_relations', name=monkey_name))

@app.route('/removebestfriend/<monkey_name>')
def delete_best_friend(monkey_name):
    monkey = Monkey.query.filter_by(name=monkey_name).first()
    monkey.remove_best_friend()
    db.session.add(monkey)
    db.session.commit()
    return redirect(url_for('show_relations', name=monkey_name))

@app.route('/delete/<name>')
def delete(name):
    monkey = Monkey.query.filter_by(name=name).first()
    for friend in list(monkey.friends):
        monkey.remove_friend(friend)
    db.session.delete(monkey)
    db.session.commit()
    return redirect(url_for('index'))
