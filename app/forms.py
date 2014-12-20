from flask.ext.wtf import Form
from wtforms import StringField, IntegerField, PasswordField
from wtforms.validators import Email, DataRequired, Length, NumberRange, \
                               ValidationError
from app.models import Monkey

def unique_name(form, field):
    if Monkey.query.filter_by(name=field.data).first():
        raise ValidationError("Name '{0}' is already used".format(field.data))

def unique_email(form, field):
    if Monkey.query.filter_by(email=field.data).first():
        raise ValidationError("Email '{0}' is already used".format(field.data))

class RegistrationForm(Form):
    name = StringField('Name', validators=[DataRequired(),
                       Length(min=3, max=64), unique_name])
    email = StringField('Email', validators=[Email(), unique_email])
    age = IntegerField('Age', validators=[DataRequired(),
                       NumberRange(min=13, max=150)])

class EditForm(Form):
    name = StringField('Name', validators=[DataRequired(),
                       Length(min=3, max=64)])
    email = StringField('Email', validators=[Email()])
    age = IntegerField('Age', validators=[DataRequired(),
                       NumberRange(min=13, max=150)])
