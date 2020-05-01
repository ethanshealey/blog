from flask_wtf import FlaskForm
from wtforms import Form as NoCsrfForm, StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectMultipleField, IntegerField, FieldList, FormField
from wtforms.validators import DataRequired, Length
from wtforms.widgets import HiddenInput

class LoginForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField('Login')

class PostForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    subtitle = StringField()
    raw_body = TextAreaField(validators=[DataRequired()])
    tags = StringField()
    submit = SubmitField('Post')

class ContactForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    email = StringField(validators=[DataRequired()])
    phone = StringField(validators=[DataRequired()])
    message = TextAreaField(validators=[DataRequired()])
    submit = SubmitField()

class SearchForm(FlaskForm):
    item = StringField(validators=[DataRequired()])
    submit = SubmitField('Search')