# coding: utf-8
import os
# from requests_oauthlib import OAuth1Session
# import json
import twitter

# from app import *
# db.create_all()
# # from app import User
#
# me = User('hito_waft', '73703740-Ia2ykBPskKGI8KRRC3GmeGJLnDYSNFn40JWlusC67', "exwOchuPiw0doJQo5qoxrrWOxSvRrnVaxECNubeBjAOYC", "73703740")
# db.session.add(me)
# db.session.commit()
#
# logined_user = User.query.filter_by(user_name=)

consumer_key = os.environ["CONSUMER_KEY"]
consumer_secret = os.environ["CONSUMER_SECRET"]

access_token = ""
access_token_secret = ""

api = twitter.Api(consumer_key=consumer_key,
                      consumer_secret=consumer_secret,
                      access_token_key=access_token,
                      access_token_secret=access_token_secret)


friends = set(api.GetFriendIDsPaged()[2])
followers = set(api.GetFollowerIDsPaged()[2])
# print([u.name for u in users])

followEachOtherSet = friends & followers

for users in followEachOtherSet:
    u = api.GetUser(users)
    print("name: %s, screen name: %s" % (u.name, u.screen_name))
