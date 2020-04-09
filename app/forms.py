from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField('Login')

class PostForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    subtitle = StringField()
    raw_body = TextAreaField(validators=[DataRequired()])
    submit = SubmitField('Post')

class ContactForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    email = StringField(validators=[DataRequired()])
    phone = StringField(validators=[DataRequired()])
    message = TextAreaField(validators=[DataRequired()])
    submit = SubmitField()