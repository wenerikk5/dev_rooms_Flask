from wtforms import StringField, TextAreaField, PasswordField
from wtforms.validators import InputRequired, NumberRange, EqualTo
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired


class RegistrationForm(FlaskForm):
    username = StringField('Username', [InputRequired()])
    name = StringField('Name')
    password = PasswordField(
        'Password',
        [InputRequired(), EqualTo('confirm', message='Passwords must match')]
    )
    confirm = PasswordField('Confirm Password', [InputRequired()])


class LoginForm(FlaskForm):
    username = StringField('Username', [InputRequired()])
    password = PasswordField('Password', [InputRequired()])


class RoomForm(FlaskForm):
    head = StringField('Head', [InputRequired()])
    description = TextAreaField('Description')
    link = StringField('Link')
    topic = StringField(
        'Topic',
        validators=[InputRequired()]
        # coerce=int
    )
    image = FileField(
        'Image',
    )
