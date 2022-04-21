from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField, SelectMultipleField, widgets, SelectField
from flask_wtf.file import FileAllowed, FileField
from wtforms.validators import Email, Length, DataRequired



class RegisterForm(FlaskForm):
    login = StringField("Login", validators=[DataRequired(), Length(min=4, max=15)])
    email = StringField("Email", validators=[DataRequired(), Email("Nie poprawny email")])
    password = PasswordField("Hasło", validators=[DataRequired(), Length(min=4, max=15)])
    submit = SubmitField("Zarejestruj się")

class LoginForm(FlaskForm):
    login = StringField("Login", validators=[DataRequired()])
    password = PasswordField("Hasło", validators=[DataRequired()])
    remember = BooleanField("Zapamietaj mnie")
    submit = SubmitField("Login")

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class UpadeInfoForm(FlaskForm):
    name =StringField("Imie", validators=[DataRequired()])
    surname = StringField("Nazwisko", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email(message="Niepoprawny email")])
    age =IntegerField("Wiek", validators=[DataRequired()])
    experience = SelectField('Doświadczenie', validators=[DataRequired()], 
                            choices=[('Małe', 'Małe'),('Średnie', 'Średnie'),('Duże' ,'Duże')])
    picture = FileField("Zdjęcie profilowe", validators=[FileAllowed(['jpg', 'png'])])
    tags = MultiCheckboxField('Tagi', coerce=int)

class UpadeInfoForm2(FlaskForm):
    about = TextAreaField("O mnie", validators=[DataRequired()])

class AddCommentForm(FlaskForm):
    comment = TextAreaField("Komentarz", validators=[DataRequired()])

class RatingForm(FlaskForm):
    rating = IntegerField("Ocena", validators=[DataRequired()])

class AddPhotoForm(FlaskForm):
    photo = FileField("Zdjęcie", validators=[FileAllowed(['jpg', 'png'])])
    tags = MultiCheckboxField("Tag", coerce=int)

class SearchTagForm(FlaskForm):
    tag = SelectField("Tag", validators=[DataRequired()], choices=[])

class AddTagForm(FlaskForm):
    name = StringField("Nazwa", validators=[DataRequired()])

class RequestResetForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Odzyskaj hasło")

class ResetPasswordForm(FlaskForm):
    password = PasswordField("Hasło", validators=[DataRequired()])      
    submit = SubmitField("Zmień hasło")