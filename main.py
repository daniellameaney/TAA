#!/usr/bin/env python

import csv
import urllib.request
import codecs
import tweepy
import json

# authenticate Tweepy with Twitter credentials
auth = tweepy.OAuthHandler('XXX', 'XXX')
auth.set_access_token('XXX', 'XXX')

# intending to pull back circa 500k tweets, this will prevent the program from exiting due to Twitter rate limiting
api = tweepy.API(auth, wait_on_rate_limit=True)

# fetching the input .csv, loads and transforms to utf-8 string to python's csv DictReader
response = urllib.request.urlopen('https://www.politics-social.com/api/list/csv/followers')
cr = csv.DictReader(codecs.iterdecode(response, 'utf-8'))

# initialising an empty dictionary for storing each MP's tweets and user info (1 MP = 1 row of data)
data = {}

# loop  through the input .csv and extracts the MP's twitter handle (under column title = Screen Name)
for row in cr:
    twitter_handle = row['Screen name']

    # it then calls the Twitter API for the current twitter_handle..
    try:
        twitter_item = api.get_user(twitter_handle)
    except:
        # .. then skips to next user if an error occurs
        continue

    # initialises a sub-dictionary, the key is the Twitter handle as 1 MP = 1 row.
    # key = twitter_handle, and additional data such as name, party, constituency, and user info are added from .csv

    data[twitter_handle] = {}
    data[twitter_handle]['Name'] = row['Name']
    data[twitter_handle]['Party'] = row['Party']
    data[twitter_handle]['Constituency'] = row['Constituency']

    # following this is a twitter API call with a new key called UserInfo
    # which dumps the raw twitter API user info (eg profile pic, follower count) in as json
    data[twitter_handle]['UserInfo'] = twitter_item._json

    # initialise a new key called Tweets, which is an array intended to contain X tweets per MP
    data[twitter_handle]['Tweets'] = []

    # loop through the users tweets and append each tweet to Tweets array (for 100 most recent tweets)
    try:
        for tweet in tweepy.Cursor(api.user_timeline, id=twitter_handle).items(100):
            data[twitter_handle]['Tweets'].append(tweet._json)
    except:
        # skips to next user if error occurs
        continue

    # converts the above dictionary to json (re: json.dumps), printing raw json to screen
    # this is output to a file and loaded into SnowFlake
    print(json.dumps(data[twitter_handle]))
