from rake_nltk import Rake
from twitter_api import TwitterAPI
from textblob import TextBlob
import random
import urllib
from nltk.tag import pos_tag

r = Rake(min_length=1, max_length=1)
twitter = TwitterAPI()

def add_polarity(tweets):
	for tw in tweets:
		blob = TextBlob(tw['text'])
		tw['polarity'] = blob.sentiment.polarity

def make_spread_package(tweets, maxpolar=1.0):
	buckets = [(-maxpolar, -maxpolar/2), (-maxpolar/2, 0), (0, maxpolar/2), (maxpolar/2, maxpolar)]
	print(buckets)

	tweet_buckets = [[], [], [], []]

	for tw in tweets:
		for i, b in enumerate(buckets):
			if tw['polarity'] >= b[0] and tw['polarity'] < b[1]:
				tweet_buckets[i].append(tw)

	min_size = min(len(tweet_buckets[0]), len(tweet_buckets[1]), len(tweet_buckets[2]), len(tweet_buckets[3]))

	tweet_buckets[0] = tweet_buckets[0][:min_size]
	tweet_buckets[1] = tweet_buckets[1][:min_size]
	tweet_buckets[2] = tweet_buckets[2][:min_size]
	tweet_buckets[3] = tweet_buckets[3][:min_size]

	result = tweet_buckets[0] + tweet_buckets[1] + tweet_buckets[2] + tweet_buckets[3]

	random.shuffle(result)

	return result

def get_tweet_package(query, maxpolar):
	tweets = twitter.get_tweets(query)

	add_polarity(tweets)

	tweets = make_spread_package(tweets, maxpolar=maxpolar)

	return tweets