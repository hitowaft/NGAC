# coding: utf-8

import os
import json
from urllib.parse import parse_qsl

from flask import Flask, session, jsonify, request, render_template, redirect
from requests_oauthlib import OAuth1Session
from flask_sqlalchemy import SQLAlchemy
# from flask.ext.session import Session

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

base_json_url = 'https://api.twitter.com/1.1/%s.json'
user_timeline_url = base_json_url % ('statuses/user_timeline')

# データベース
from sqlalchemy.engine import Engine
from sqlalchemy import event

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()

db_uri = "sqlite:///" + os.path.join(app.root_path, 'development.db') # 追加
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri # 追加
db = SQLAlchemy(app) # 追加

class User(db.Model): # 追加
    __tablename__ = "users" # 追加
    id = db.Column(db.Integer, primary_key=True) # 追加
    user_name = db.Column(db.String(), nullable=False)
    oauth_token = db.Column(db.String(), nullable=False) # 追加
    oauth_token_secret = db.Column(db.String(), nullable=False)
    user_id = db.Column(db.Integer, nullable=False, unique=True)

    def __init__(self, user_name, oauth_token, oauth_token_secret, user_id):
        self.user_name = user_name
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
        self.user_id = user_id


@app.route('/', methods=["GET", "POST"])
def index():
    if 'user_name' in session:
        message = 'Hello ' + str(session['user_name'])
    else:
        message = 'ログインしていません'
    return render_template("test.html", message=message)

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
    # return jsonify(request_token)



# アクセストークン（連携したユーザーとしてTwitterのAPIを叩くためのトークン）を返すAPI
@app.route('/auth/twitter/callback', methods=['GET'])
def get_twitter_access_token():

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

    # return jsonify(access_token)
    session["user_id"] = access_token["user_id"]
    session["user_name"] = access_token["screen_name"]

    return redirect("/")

    # user = User(access_token["screen_name"], access_token["oauth_token"], access_token["oauth_token_secret"], access_token["user_id"])
    # db.session.add(user)
    # db.session.commit()
    # users = User.query.all()
    # return users[0]

    # return access_token["oauth_token"]

# @app.route('/twitter/user_timeline', methods=['GET'])
# def get_twitter_user_timeline():
#
#     access_token = request.args.get('access_token')
#
#     params = {
#         'user_id': request.args.get('user_id'),
#         'exclude_replies': True,
#         'include_rts': json.get('include_rts', False),
#         'count': 20,
#         'trim_user': False,
#         'tweet_mode': 'extended',    # full_textを取得するために必要
#     }
#
#     twitter = OAuth1Session(
#         consumer_key,
#         consumer_secret,
#         access_token['oauth_token'],
#         access_token['oauth_token_secret'],
#     )
#
#     response = twitter.get(user_timeline_url, params=params)
#     results = json.loads(response.text)
#
#     return jsonify(results)

if __name__ == "__main__":
    port = os.environ.get('PORT', 8080)
    app.run(
        host='0.0.0.0',
        port=port,
    )
