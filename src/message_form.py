#入力フォームのバリデーション
from flask_wtf import FlaskForm
from wtforms import TextAreaField, validators

class MessageForm(FlaskForm):
    invite_message = TextAreaField('117文字以下で招待文を入力して下さい', [validators.Length(min=1, max=117)])

    def validate_message(self, invite_message):
        if len(invite_message.data) > 117:
            raise ValidationError("117文字以下で入力してください")
