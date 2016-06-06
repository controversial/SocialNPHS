"""
Get authenticated tweepy API object
"""

import json
import os

import tweepy

localdir = os.getcwd()


def _get_secret_stuffs():
    """ Retrieves Twitter API tokens & keys from stored secrets """
    secrets = ["CONSUMER_KEY",
               "CONSUMER_SECRET",
               "ACCESS_TOKEN",
               "ACCESS_SECRET"]
    with open(os.path.join(localdir, "token.json")) as f:
        t = json.load(f)
        return [t[s] for s in secrets]


def _get_api():
    """ Gets an authenticated tweepy API instance from stored JSON secrets """
    secrets = _get_secret_stuffs()
    auth = tweepy.OAuthHandler(*secrets[:2])
    auth.set_access_token(*secrets[2:])
    return tweepy.API(auth)

api = _get_api()
