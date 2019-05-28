#入力フォームのバリデーション
from flask_wtf import FlaskForm
from wtforms import TextAreaField, validators, SubmitField

class MessageForm(FlaskForm):
    invite_message = TextAreaField('140文字以内で招待文を入力して下さい', [validators.Length(min=1, max=140)])
    decline_message = TextAreaField()
    submit = SubmitField('確認する')

    def validate_message(self, invite_message):
        if len(invite_message.data) > 140:
            raise ValidationError("140文字以内で入力してください")

# class ContactForm(FlaskForm):
