# coding: utf-8
import os
# from requests_oauthlib import OAuth1Session
# import json
import twitter


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
