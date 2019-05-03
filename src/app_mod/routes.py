from app_mod import app
import os
from requests_oauthlib import OAuth1Session
from flask import Flask, session, request, render_template, redirect, flash

from app_mod.models import User, SelectedFollower, Message
from app_mod import db

import twitter
from urllib.parse import parse_qsl

app.secret_key = '\x11dO\xb3z\xcc\xf5^\x885\x9ah\x06\xca\x98s\xe5\xfa\xf0\xf5\r\xab\x87\x84'
# from flask_sqlalchemy import SQLAlchemy


consumer_key = os.environ["CONSUMER_KEY"]
consumer_secret = os.environ["CONSUMER_SECRET"]


base_url = 'https://api.twitter.com/'

request_token_url = base_url + 'oauth/request_token'
authenticate_url = base_url + 'oauth/authenticate'
access_token_url = base_url + 'oauth/access_token'


@app.route('/', methods=["GET", "POST"])
def top():
    if "screen_name" in session:
        message = str(session['screen_name']) + "でログイン中"
    else:
        message = 'ログインしていません'
    return render_template("top.html", message=message)

# 認証
@app.route('/twitter/request_token', methods=['GET'])
def get_twitter_request_token():

    # Twitter Application Management で設定したコールバックURLsのどれか
    oauth_callback = request.args.get(os.environ.get('APP_BASE_URL') + 'auth/twitter/callback')

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



# アクセストークンを返し、ユーザー情報をDBに入れる
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

    session["user_id"] = str(access_token["user_id"])
    session["screen_name"] = access_token["screen_name"]

    # 完全新規ユーザー
    if User.query.filter_by(user_id=session["user_id"]).first() is None:

        user = User(user_id=access_token["user_id"],  screen_name=access_token["screen_name"], oauth_token=access_token["oauth_token"], oauth_token_secret=access_token["oauth_token_secret"])

        db.session.add(user)
        db.session.commit()

        api = return_twitter_api()
        user_info = api.GetUser(user_id=session["user_id"])

        user = User.query.filter_by(user_id=session["user_id"]).first()
        user.user_name = user_info.name
        user.user_image_url = user_info.profile_image_url_https

    # 既存ユーザーアップデート
    else:
        user =  User.query.filter_by(user_id=session["user_id"]).first()

        user.user_id = access_token["user_id"]
        user.screen_name = access_token["screen_name"]
        user.oauth_token = access_token["oauth_token"]
        user.oauth_token_secret = access_token["oauth_token_secret"]

    db.session.add(user)
    db.session.commit()

    if session.get("host_id") is not None:
        return redirect("/invitation/{}".format(session["host_id"]))
    else:
        return redirect("/")

from message_form import MessageForm

@app.route('/make_invitations', methods=['GET'])
def show_mutual_following_list():
    global mutual_list
    mutual_list = return_mutual_list()

    for followers in mutual_list:
        if User.query.filter_by(user_id=str(followers[3])).first():
            continue
        else:
            user = User(user_id=followers[3], user_name=followers[0], screen_name=followers[1], user_image_url=followers[2])

            db.session.add(user)
            db.session.commit()

    return render_template("make_invitations.html", mutual_list=mutual_list)

#twitter.apiインスタンスを返す
def return_twitter_api():
    user = User.query.filter_by(user_id=session["user_id"]).first()
    access_token = user.oauth_token
    access_token_secret = user.oauth_token_secret

    api = twitter.Api(consumer_key=consumer_key,
                          consumer_secret=consumer_secret,
                          access_token_key=access_token,
                          access_token_secret=access_token_secret)

    return api

#相互フォローリストを作成
def return_mutual_list():
    api = return_twitter_api()

    friends = set(api.GetFriendIDsPaged()[2])
    followers = set(api.GetFollowerIDsPaged()[2])

    followEachOtherSet = friends & followers
    mutual_list = []

    for users in followEachOtherSet:
        u = api.GetUser(users)
        mutual_list.append([u.name, u.screen_name, u.profile_image_url_https, u.id])

    return mutual_list


@app.route('/message_and_date', methods=['GET', 'POST'])
def select_invite_message_and_date():
    form = MessageForm(request.form)

    session["selected_followers"]  = request.form.getlist("user_select")
    # if request.form["calendar"]:
    #     session["selected_date"]  = request.form["calendar"]

    global info_added_followers
    info_added_followers = []
    for follower_id in session["selected_followers"]:
        user = User.query.filter_by(user_id=follower_id).first()
        info_added_followers.append(user)

    # if not form.validate():
    #     flash("127文字以下で入力してください")
    #     return redirect("/make_invitations")
    # else:
    #     invite_test = form.invite_message.data
    # if not form.validate_on_submit():
    #     flash("メッセージは127文字以下で入力してください")
    #     return redirect('/message_and_date')

    # session["invite_message"]  = request.form["invite_message"]
    # session["selected_date"]  = request.form["calendar"]
    # session["decline_message"]  = request.form["decline_message"]


    return render_template("/message_and_date.html", info_added_followers=info_added_followers, form=form)

import datetime

@app.route('/message_confirmation', methods=["GET", "POST"])
def message_confirmation():
    form = MessageForm(request.form)
    if not form.validate_on_submit():
        flash("メッセージは127文字以下で入力してください")

        return render_template("/message_and_date.html", form=form)

    for selected_follower in session["selected_followers"]:
        if SelectedFollower.query.filter_by(selected_follower_id=selected_follower, user_id=session["user_id"]).first():
            continue
        else:
            sf = SelectedFollower(selected_follower_id=selected_follower, user_id=session["user_id"])
            db.session.add(sf)


    selected_followers = SelectedFollower.query.filter_by( user_id=session["user_id"]).all()
    session["invite_message"]  = request.form["invite_message"]
    session["selected_date"]  = datetime.datetime.strptime(request.form["calendar"], "%Y-%m-%d")
    session["decline_message"]  = request.form["decline_message"]

    messages = Message(invite_message=session["invite_message"], expiration_date=session["selected_date"],  decline_message=request.form["decline_message"], user_id=session["user_id"])
    db.session.add(messages)

    db.session.commit()

    return render_template("/message_confirmation.html", selected_followers = selected_followers, invite_message=session["invite_message"], selected_date=session["selected_date"], decline_message=session["decline_message"])

@app.route('/message_posting', methods=["GET", "POST"])
def message_posting():
    api = return_twitter_api()
    api.PostUpdate(session["invite_message"] + " {}invitation/{}".format(os.environ.get('APP_BASE_URL'), session["user_id"]))

    return render_template("/post_updated.html")

# @app.route('/post_updated', methods=["GET"])
# def post_updated():



@app.route('/show_result/<user_id>', methods=["GET"])
def show_result(user_id):

    return render_template("/show_result.html")

@app.route('/invitation/<host_id>', methods=["GET"])
def show_invitation(host_id):
    if Message.query.filter_by(user_id=host_id).first() is None:
        return "URLが無効です"

    session["host_id"] = host_id

    if session.get("user_id") is None:
        login_status = "not_logged_in"
        return render_template("/invitation.html", login_status=login_status)

    elif session.get("user_id") == session["host_id"]:
        return redirect("/")

    else:
        api = return_twitter_api()

        guest_user = api.GetUser(user_id=session["user_id"])
        host_user = User.query.filter_by(user_id=host_id).first()

        result = SelectedFollower.query.filter_by(user_id=host_id, selected_follower_id=session["user_id"]).first()

        if result != None:
            api = return_twitter_api()
            api.PostDirectMessage("{}(@{})さんもあなたに会いたがっています！".format(guest_user.name, guest_user.screen_name), user_id=host_user.user_id)

            decline_message = None
        else:
            decline_message = Message.query.filter_by(user_id=host_id).first().decline_message

        return render_template("/invitation.html", result=result, decline_message=decline_message)
