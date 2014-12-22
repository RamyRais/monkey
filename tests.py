#!flask/bin/python
import os
import unittest

from config import basedir
from app import app, db
from app.models import Monkey
from coverage import coverage

cov = coverage(branch=True, omit=['flask/*', 'tests.py'])
cov.start()


class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def add_monkey(self,name,email,age):
    	return self.app.post('/addmonkey', data=dict(name=name,
                      email=email, age=age), follow_redirects=True)
    
    def view_profile(self,name):
        return self.app.get('/profile/{0}'.format(name),follow_redirects=True)
    
    def edit_profile(self,name,changedName,email,age):
        return self.app.post('/profile/{0}/edit'.format(name),data=dict(
            name=changedName, email=email, age=age), follow_redirects=True)
    
    def test_edit_profile(self):
        m1 = Monkey(name='ramy', email='ramy@gmail.com', age='20')
        db.session.add(m1)
        db.session.commit()
        m2 = Monkey(name='ramy1', email='ramy1@gmail.com', age='20')
        db.session.add(m2)
        db.session.commit()
        rv = self.edit_profile("ramy","ramy","ramy@gmail.com","20")
        assert "ramy" in rv.data
        assert "ramy@gmail.com" in rv.data
        assert "20" in rv.data
        rv = self.edit_profile("ramy","ramy2","ramy@gmail.com","20")
        assert Monkey.query.filter_by(name="ramy2").count() == 1
        assert "ramy2" in rv.data
        assert "ramy@gmail.com" in rv.data
        assert "20" in rv.data
        rv = self.edit_profile("ramy2","ramy2","ramy2@gmail.com","20")
        assert Monkey.query.filter_by(email="ramy2@gmail.com").count() == 1
        assert "ramy2" in rv.data
        assert "ramy2@gmail.com" in rv.data
        assert "20" in rv.data
        rv = self.edit_profile("ramy2","ramy2","ramy2@gmail.com","25")
        assert "ramy2" in rv.data
        assert "ramy2@gmail.com" in rv.data
        assert "25" in rv.data
        rv = self.edit_profile("ramy2","ramy1","ramy1@gmail.com","20")
        assert Monkey.query.filter_by(name="ramy1").count() == 1
        #print rv.data
        assert "Name ramy1 is already used" in rv.data
        assert "Email ramy1@gmail.com is already used" in rv.data
        assert "20" in rv.data
        


    def test_view_profile(self):
        m1 = Monkey(name='ramy', email='ramy@gmail.com', age='20')
        db.session.add(m1)
        db.session.commit()
        rv = self.view_profile('ramy')
        assert "ramy" in rv.data
        assert "ramy@gmail.com" in rv.data
        assert "20" in rv.data
        # redirection pour monkey that doesn't exist
        rv = self.view_profile('test')
        assert "Add Monkey" in rv.data

    def test_add_monkey(self):
    	#testin a simple add of a monkey
        rv = self.add_monkey('ramy','ramy@gmail.com','20')
        assert Monkey.query.filter_by(name='ramy').count() == 1
        assert len(Monkey.query.all()) == 1
        #testing the unicity of the name
        rv = self.add_monkey('ramy','ramy1@gmail.com','25')
        assert "Name &#39;ramy&#39; is already used" in rv.data
        assert Monkey.query.filter_by(name='ramy').count() == 1
        #testing the unicity of the Email
        rv = self.add_monkey('ramy1','ramy@gmail.com','30')
        assert "Email &#39;ramy@gmail.com&#39; is already used" in rv.data
        assert Monkey.query.filter_by(
            email='ramy@gmail.com').count() == 1
        #testing the length of the name should be greater than 2 caracters
        rv = self.add_monkey('ra','ra@gmail.com','20')
        assert "Field must be between 3 and 64 characters long." in rv.data
        assert Monkey.query.filter_by(name='ra').count() == 0
        #testing the length of the name should be less than 65 caracters
        rv = self.add_monkey(
            'azertyuiopmlkjhgfdsqwxcvbnazertyuiopmlkjhgfdsqwxcvbnazertyuiopmlk',
            'ra@gmail.com','20')
        assert "Field must be between 3 and 64 characters long." in rv.data
        assert Monkey.query.filter_by(name='ra@gmail.com').count() == 0
        #testing the email format
        rv = self.add_monkey('ramy2','ramy','50')
        assert "Invalid email address." in rv.data
        assert Monkey.query.filter_by(email='ramy').count() == 0
        #testing the age should be greater than 12
        rv = self.add_monkey('ramy3','ramy3@gmail.com','10')
        assert"Number must be between 13 and 150." in rv.data
        assert Monkey.query.filter_by(name='ramy3').count() == 0
        #testing the age should be less than 151
    	rv = self.add_monkey('ramy3','ramy3@gmail.com','200')
        assert"Number must be between 13 and 150." in rv.data
        assert Monkey.query.filter_by(name='ramy3').count() == 0

if __name__ == '__main__':
    try:
        unittest.main()
    except:
        pass
    cov.stop()
    cov.save()
    print "\n\nCoverage Report:\n"
    cov.report()
    print "HTML version: " + os.path.join(basedir, "tmp/coverage/index.html")
    cov.html_report(directory='tmp/coverage')
    cov.erase()