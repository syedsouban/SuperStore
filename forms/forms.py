from flask_wtf import FlaskForm as Form
from wtforms.fields import StringField, SubmitField
from wtforms.validators import Required


class LoginForm(Form):
    """Accepts a nickname and a room."""
    name = StringField('Name', validators=[Required()])
    room = StringField('Room', validators=[Required()])
    submit = SubmitField('Enter Chatroom')

class SigninForm(Form):
    """Accepts a nickname and a room."""
    email = StringField('emailaddress', validators=[Required()])
    password = StringField('password', validators=[Required()])
    submit = SubmitField('Login')
