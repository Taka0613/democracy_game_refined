from wtforms import Form, StringField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired


class LoginForm(Form):
    character_name = StringField("Character Name", validators=[DataRequired()])
    submit = SubmitField("Login")


class ProjectInsightForm(Form):
    include_insight = BooleanField("Include Your Character’s Insight")
    insight_description = TextAreaField("Describe Your Insight")
    submit = SubmitField("Submit Project")
