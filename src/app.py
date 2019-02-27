# coding: utf-8

import os
import twitter
from urllib.parse import parse_qsl

from flask import Flask, session, request, render_template, redirect
from requests_oauthlib import OAuth1Session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["DEBUG"] = True
SESSION_TYPE = 'redis'
app.config.from_object(__name__)
app.secret_key = os.urandom(24)
# Session(app)

consumer_key = os.environ["CONSUMER_KEY"]
consumer_secret = os.environ["CONSUMER_SECRET"]


base_url = 'https://api.twitter.com/'

request_token_url = base_url + 'oauth/request_token'
authenticate_url = base_url + 'oauth/authenticate'
access_token_url = base_url + 'oauth/access_token'

# データベース
from sqlalchemy.engine import Engine
from sqlalchemy import event

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()

db_uri = "sqlite:///" + os.path.join(app.root_path, 'development.db')
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(), nullable=False)
    oauth_token = db.Column(db.String(), nullable=False)
    oauth_token_secret = db.Column(db.String(), nullable=False)
    user_id = db.Column(db.Integer, nullable=False, unique=True)

    def __init__(self, user_name, oauth_token, oauth_token_secret, user_id):
        self.user_name = user_name
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
        self.user_id = user_id


@app.route('/', methods=["GET", "POST"])
def top():
    if 'user_name' in session:
        message = 'Hello, ' + str(session['user_name'])
    else:
        message = 'ログインしていません'
    return render_template("top.html", message=message)

# 認証画面（「このアプリと連携しますか？」の画面）のURLを返すAPI
@app.route('/twitter/request_token', methods=['GET'])
def get_twitter_request_token():

    # Twitter Application Management で設定したコールバックURLsのどれか
    oauth_callback = request.args.get('http://0.0.0.0:8080/auth/twitter/callback')

    twitter = OAuth1Session(consumer_key, consumer_secret)

    response = twitter.post(
        request_token_url,
        params={'oauth_callback': oauth_callback}
    )

    request_token = dict(parse_qsl(response.content.decode("utf-8")))

    # リクエストトークンから認証画面のURLを生成
    authenticate_endpoint = '%s?oauth_token=%s' \
        % (authenticate_url, request_token['oauth_token'])

    request_token.update({'authenticate_endpoint': authenticate_endpoint})

    return redirect(authenticate_endpoint)



# アクセストークン（連携したユーザーとしてTwitterのAPIを叩くためのトークン）を返すAPI
@app.route('/auth/twitter/callback', methods=['GET'])
def get_twitter_access_token():

    if request.args.get('denied'): #認証をキャンセルしたらトップに戻る
        return redirect("/")

    oauth_token = request.args.get('oauth_token')
    oauth_verifier = request.args.get('oauth_verifier')

    twitter = OAuth1Session(
        consumer_key,
        consumer_secret,
        oauth_token,
        oauth_verifier,
    )

    response = twitter.post(
        access_token_url,
        params={'oauth_verifier': oauth_verifier}
    )

    access_token = dict(parse_qsl(response.content.decode("utf-8")))

    session["user_id"] = access_token["user_id"]
    session["user_name"] = access_token["screen_name"]

    if User.query.filter_by(user_id=session["user_id"]).first() is None:
        user = User(access_token["screen_name"], access_token["oauth_token"], access_token["oauth_token_secret"], access_token["user_id"])
        db.session.add(user)
        db.session.commit()

    return redirect("/mutual_following_list")


@app.route('/mutual_following_list', methods=['GET'])
def show_mutual_following_list():
    mutual_list = return_mutual_list()

    return render_template("mutual_following_list.html", mutual_list=mutual_list)

def return_mutual_list():
    user = User.query.filter_by(user_id=session["user_id"]).first()
    access_token = user.oauth_token
    access_token_secret = user.oauth_token_secret

    api = twitter.Api(consumer_key=consumer_key,
                          consumer_secret=consumer_secret,
                          access_token_key=access_token,
                          access_token_secret=access_token_secret)


    friends = set(api.GetFriendIDsPaged()[2])
    followers = set(api.GetFollowerIDsPaged()[2])
    # print([u.name for u in users])

    followEachOtherSet = friends & followers
    mutual_list = []

    for users in followEachOtherSet:
        u = api.GetUser(users)
        mutual_list.append([u.name, u.screen_name, u.profile_image_url_https])

    return mutual_list

# @app.route('/message_and_date', methods=['GET', 'POST'])
# def select_invite_message_and_date():




if __name__ == "__main__":
    port = os.environ.get('PORT', 8080)
    app.run(
        host='0.0.0.0',
        port=port,
    )
