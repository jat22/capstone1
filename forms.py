from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, RadioField, DateField
from wtforms.validators import DataRequired, Email, Length


class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=20)])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=20)])

class NewTripForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    start_date = DateField("Start Date")
    end_date = DateField("End Date")
    comments = TextAreaField("Comments")