# coding: utf-8

import os
# import twitter
# from urllib.parse import parse_qsl

# from flask import Flask, session, request, render_template, redirect, flash
# from requests_oauthlib import OAuth1Session
# from flask_sqlalchemy import SQLAlchemy
from app_mod import app

# app = Flask(__name__)
# app.config["DEBUG"] = True
# SESSION_TYPE = 'redis'
# app.config.from_object(__name__)
# app.secret_key = os.urandom(24)
# Session(app)


# consumer_key = os.environ["CONSUMER_KEY"]
# consumer_secret = os.environ["CONSUMER_SECRET"]
#
#
# base_url = 'https://api.twitter.com/'
#
# request_token_url = base_url + 'oauth/request_token'
# authenticate_url = base_url + 'oauth/authenticate'
# access_token_url = base_url + 'oauth/access_token'

# # データベース
# from sqlalchemy.engine import Engine
# from sqlalchemy import event
#
# @event.listens_for(Engine, "connect")
# def set_sqlite_pragma(dbapi_connection, connection_record):
#     cursor = dbapi_connection.cursor()
#     cursor.execute("PRAGMA journal_mode=WAL")
#     cursor.close()
#
# db_uri = "sqlite:///" + os.path.join(app.root_path, 'development.db')
# app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
# db = SQLAlchemy(app)
#
# class User(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     screen_name = db.Column(db.String(), nullable=False)
#     oauth_token = db.Column(db.String(), nullable=False)
#     oauth_token_secret = db.Column(db.String(), nullable=False)
#     user_id = db.Column(db.Integer, nullable=False, unique=True)
#
#     def __init__(self, screen_name, oauth_token, oauth_token_secret, user_id):
#         self.screen_name = screen_name
#         self.oauth_token = oauth_token
#         self.oauth_token_secret = oauth_token_secret
#         self.user_id = user_id
#
# class SelectedFollower(db.Model):
#     __tablename__ = "selected_followers"
#     id = db.Column(db.Integer, primary_key=True)
#     selected_follower_list = db.Column(db.Integer, nullable=False)
#     selected_date = db.Column(db.DateTime(), nullable=True)
#     user_id = db.Column(db.Integer, nullable=False, unique=True), db.ForeignKey('user.user_id')
#
#     def __init__(self, selected_follower_list, selected_date, user_id):
#         self.selected_follower_list = selected_follower_list
#         self.selected_date = selected_date
#         self.user_id = user_id
#
#     db.create_all()


# @app.route('/', methods=["GET", "POST"])
# def top():
#     if 'screen_name' in session:
#         message = 'Hello, ' + str(session['screen_name'])
#     else:
#         message = 'ログインしていません'
#     return render_template("top.html", message=message)
#
# # 認証画面（「このアプリと連携しますか？」の画面）のURLを返すAPI
# @app.route('/twitter/request_token', methods=['GET'])
# def get_twitter_request_token():
#
#     # Twitter Application Management で設定したコールバックURLsのどれか
#     oauth_callback = request.args.get('http://0.0.0.0:8080/auth/twitter/callback')
#
#     twitter = OAuth1Session(consumer_key, consumer_secret)
#
#     response = twitter.post(
#         request_token_url,
#         params={'oauth_callback': oauth_callback}
#     )
#
#     request_token = dict(parse_qsl(response.content.decode("utf-8")))
#
#     # リクエストトークンから認証画面のURLを生成
#     authenticate_endpoint = '%s?oauth_token=%s' \
#         % (authenticate_url, request_token['oauth_token'])
#
#     request_token.update({'authenticate_endpoint': authenticate_endpoint})
#
#     return redirect(authenticate_endpoint)
#
#
#
# # アクセストークン（連携したユーザーとしてTwitterのAPIを叩くためのトークン）を返すAPI
# @app.route('/auth/twitter/callback', methods=['GET'])
# def get_twitter_access_token():
#
#     if request.args.get('denied'): #認証をキャンセルしたらトップに戻る
#         return redirect("/")
#
#     oauth_token = request.args.get('oauth_token')
#     oauth_verifier = request.args.get('oauth_verifier')
#
#     twitter = OAuth1Session(
#         consumer_key,
#         consumer_secret,
#         oauth_token,
#         oauth_verifier,
#     )
#
#     response = twitter.post(
#         access_token_url,
#         params={'oauth_verifier': oauth_verifier}
#     )
#
#     access_token = dict(parse_qsl(response.content.decode("utf-8")))
#
#     session["user_id"] = access_token["user_id"]
#     session["screen_name"] = access_token["screen_name"]
#
#     if User.query.filter_by(user_id=session["user_id"]).first() is None:
#         user = User(access_token["screen_name"], access_token["oauth_token"], access_token["oauth_token_secret"], access_token["user_id"])
#         db.session.add(user)
#         db.session.commit()
#
#     return redirect("/")
#
# from message_form import MessageForm
#
# @app.route('/make_invitations', methods=['GET'])
# def show_mutual_following_list():
#     mutual_list = return_mutual_list()
#
#     #validation付きフォーム
#     form = MessageForm(request.form)
#
#     return render_template("make_invitations.html", mutual_list=mutual_list, form=form)
#
# #相互フォローリストを作成
# def return_mutual_list():
#     user = User.query.filter_by(user_id=session["user_id"]).first()
#     access_token = user.oauth_token
#     access_token_secret = user.oauth_token_secret
#
#     api = twitter.Api(consumer_key=consumer_key,
#                           consumer_secret=consumer_secret,
#                           access_token_key=access_token,
#                           access_token_secret=access_token_secret)
#
#
#     friends = set(api.GetFriendIDsPaged()[2])
#     followers = set(api.GetFollowerIDsPaged()[2])
#
#     followEachOtherSet = friends & followers
#     mutual_list = []
#
#     for users in followEachOtherSet:
#         u = api.GetUser(users)
#         mutual_list.append([u.name, u.screen_name, u.profile_image_url_https, u.id])
#
#     return mutual_list
#
#
# @app.route('/message_and_date', methods=['GET', 'POST'])
# def select_invite_message_and_date():
#     selected_user = request.form.getlist("user_select")
#     # invite_message = request.form["invite_message"]
#     selected_date = request.form["calendar"]
#     decline_message = request.form["decline_message"]
#
#     form = MessageForm(request.form["invite_message"])
#
#     if not form.validate():
#         flash("117文字以下で入力してください")
#         return redirect("/make_invitations")
#     else:
#         invite_test = form.invite_message.data
#
#     return render_template("/message_and_date.html", selected_user=selected_user, invite_message=invite_test, date=selected_date, decline_message=decline_message)
#     # ここでデータベースにユーザーリストとメッセージと日時を追加する
#
#
# @app.route('/show_result/<screen_name>', methods=["GET"])
# def show_result(screen_name):
#
#     return render_template("/show_result.html")
#
# @app.route('/invitation/<screen_name>', methods=["GET"])
# def show_invitation(screen_name):
#
#     return render_template("/invitation.html")



if __name__ == "__main__":
    port = os.environ.get('PORT', 8080)
    app.run(
        host='0.0.0.0',
        port=port,
    )
