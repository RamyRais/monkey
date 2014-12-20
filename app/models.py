from app import db

class Monkey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(100), index=True, unique=True)
    age = db.Column(db.Integer)

    def __repr__(self):
        return '<Monkey {0}>'.format(name)
