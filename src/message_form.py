#入力フォームのバリデーション
from flask_wtf import FlaskForm
from wtforms import TextAreaField, validators, SubmitField

class MessageForm(FlaskForm):
    invite_message = TextAreaField('127文字以下で招待文を入力して下さい', [validators.Length(min=1, max=127)])
    decline_message = TextAreaField()
    submit = SubmitField('送信する')

    def validate_message(self, invite_message):
        if len(invite_message.data) > 127:
            raise ValidationError("127文字以下で入力してください")
