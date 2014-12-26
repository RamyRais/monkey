from flask import render_template, redirect, url_for, request
from app import app, db
from app.forms import RegistrationForm, EditForm
from app.models import Monkey, friendship
from config import MONKEYS_PER_PAGE
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func
from sqlalchemy import desc
import webhelpers.paginate as paginate

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
def index(page=1):
    sort_by = "name"
    if request.method == 'POST':
        sort_by = request.form['sort_by']    
    a1 = aliased(Monkey)
    a2 = aliased(Monkey)
    
    # This query don't work on postgres on heroku it work fine with MySql
    #monkeys = db.session.query(a1.name.label('name'),func.count(a1.name).label(
    #    'number_friend'),a2.name.label('best_friend')).outerjoin(a2,
    #    a1.best_friend == a2.id).outerjoin(friendship,a1.id ==
    #    friendship.c.monkey_id).group_by(a1.id).order_by(sort_by).all()
    
    query = "SELECT f1.name AS name, a2.name AS best_friend, f1.number_friend \
            FROM (SELECT a1.name ,a1.best_friend, COUNT(a1.name) AS \
            number_friend FROM monkey AS a1  LEFT OUTER JOIN friendship \
            ON a1.id = friendship.monkey_id GROUP BY a1.id) AS f1 \
            LEFT OUTER JOIN monkey AS a2 ON f1.best_friend = a2.id \
            ORDER BY {0}".format(sort_by)
    monkeys = db.session.execute(query).fetchall()
    monkeys = paginate.Page(monkeys,page,MONKEYS_PER_PAGE)
    return render_template("index.html", title='home', monkeys=monkeys)

@app.route('/addmonkey', methods=['GET', 'POST'])
def add_monkey():
    form = RegistrationForm()
    if form.validate_on_submit():
        monkey = Monkey()
        form.populate_obj(monkey)
        monkey.add_friend(monkey)
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
    friends.remove(monkey)
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
