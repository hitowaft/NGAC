# Herokuのスケジューラで毎日0時に実行する
from app_mod.models import SelectedFollower, Message
from app_mod import db

import datetime

# TODO: 日付が変わった時に前日が期限のデータを消去するように変更する
today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).date()

expired_messages = Message.query.filter_by(expiration_date=today).all()

for i in expired_messages:
    db.session.delete(i)

db.session.commit()
