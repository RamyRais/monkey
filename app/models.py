from app import db
from config import FRIENDS_TO_LOAD

friendship = db.Table('friendship',
    db.Column('monkey_id', db.Integer, db.ForeignKey('monkey.id')),
    db.Column('friend_id', db.Integer, db.ForeignKey('monkey.id')))

class Monkey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(100), index=True, unique=True)
    age = db.Column(db.Integer)
    friends = db.relationship('Monkey', secondary=friendship,
                               primaryjoin=(friendship.c.monkey_id == id),
                               secondaryjoin=(friendship.c.friend_id == id))
    best_friend = db.Column(db.Integer, db.ForeignKey('monkey.id'), index=True)
    bestFriend = db.relationship('Monkey', uselist=False,
                                  remote_side=id)

    def add_friend(self, monkey):
        if (type(monkey) == Monkey) and not self.is_friend_with(monkey):
            self.friends.append(monkey)
            monkey.friends.append(self)
            return self

    def remove_friend(self, monkey):
        if (type(monkey) == Monkey) and self.is_friend_with(monkey):
            if self.bestFriend == monkey:
                self.remove_best_friend()
            self.friends.remove(monkey)
            monkey.friends.remove(self)
            return self

    def is_friend_with(self, monkey):
        return monkey in self.friends

    def not_friends(self, offset=0):
        monkeys = Monkey.query.filter(Monkey.id != self.id)
        not_friends = list(set(monkeys)-set(self.friends))
        return not_friends[offset:FRIENDS_TO_LOAD]

    def make_best_friend(self, monkey):
        if not self.has_best_friend() and self.is_friend_with(monkey):
            self.bestFriend = monkey
            return self

    def remove_best_friend(self):
        if self.has_best_friend():
            self.bestFriend = None
            return self

    def has_best_friend(self):
        return self.bestFriend != None

    def __eq__(self, monkey):
        if monkey is not None:
            return self.name == monkey.name
        return False

    def __repr__(self):
        return '<Monkey {0}>'.format(self.name)

