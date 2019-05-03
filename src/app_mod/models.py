from datetime import datetime
from app_mod import db

class User(db.Model):
    __tablename__ = "users"
    # id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(),index=True, unique=True, primary_key=True)
    user_name = db.Column(db.String(), nullable=True)
    screen_name = db.Column(db.String(), nullable=False)
    user_image_url = db.Column(db.String(), nullable=True)

    #以降は主体的利用ユーザーのみの項目
    oauth_token = db.Column(db.String())
    oauth_token_secret = db.Column(db.String())
    selected_followers = db.relationship('SelectedFollower', backref='user', lazy='dynamic')
    messages = db.relationship('Message', backref='user', lazy='dynamic')

    def __repr__(self):
        return '{}(@{})'.format(self.user_name, self.screen_name)

    # def __init__(self, user_id, user_name, screen_name, user_image_url, oauth_token, oauth_token_secret):
    #     self.user_id = user_id
    #     self.user_name = user_name
    #     self.screen_name = screen_name
    #
    #     self.user_image_url = user_image_url
    #     self.oauth_token = oauth_token
    #     self.oauth_token_secret = oauth_token_secret

class SelectedFollower(db.Model):
    __tablename__ = "selected_followers"
    __table_args__ = (db.UniqueConstraint("selected_follower_id", "user_id")),

    id = db.Column(db.Integer, primary_key=True)
    selected_follower_id = db.Column(db.Integer)
    # selected_follower_name = db.Column(db.String())
    timestamp = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    user_id = db.Column(db.String(), db.ForeignKey('users.user_id'))

    def __repr__(self):
        user = User.query.filter_by(user_id=self.selected_follower_id).first()
        return 'name: {}(@{})'.format(user.user_name, user.screen_name)

    def __init__(self, selected_follower_id, user_id):
        self.selected_follower_id = selected_follower_id
        self.user_id = user_id


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    invite_message = db.Column(db.String())
    decline_message = db.Column(db.String())
    expiration_date = db.Column(db.Date())
    user_id = db.Column(db.String(), db.ForeignKey('users.user_id'))
