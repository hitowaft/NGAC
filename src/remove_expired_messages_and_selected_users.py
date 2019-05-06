# Herokuのスケジューラで毎日0時に実行する
from app_mod.models import SelectedFollower, Message
from app_mod import db

from datetime import datetime, date, timedelta, timezone

yesterday = datetime.now(timezone(timedelta(hours=9))).date() - timedelta(days=1)

expired_messages = Message.query.filter_by(expiration_date=yesterday).all()

for i in expired_messages:
    # selected_followerテーブルの期限切れ選択済みユーザーを削除
    expired_wanna_meet_list = SelectedFollower.query.filter_by(user_id=i.user_id).all()
    for j in expired_wanna_meet_list:
        db.session.delete(j)

    # messageテーブルの期限切れデータを削除
    db.session.delete(i)


db.session.commit()
