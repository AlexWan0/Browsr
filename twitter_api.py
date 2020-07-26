import tweepy
import api_keys
import pickle
import re
import time
from unidecode import unidecode
from filter_toxic import create_filtered
from tqdm import tqdm

class TwitterAPI():
	def __init__(self):
		auth = tweepy.auth.OAuthHandler(api_keys.CONSUMER_KEY, api_keys.CONSUMER_SECRET)
		auth.set_access_token(api_keys.ACCESS_KEY, api_keys.ACCESS_SECRET)
		self.api = tweepy.API(auth)

	def post_process(self, text):
		text = unidecode(text)
		text = re.sub(r'(?:https?|ftp):\/\/[\n\S]+', '', text)
		return text

	def get_tweets(self, query, out_path='db.pkl', use_cache=True):
		with open('db_filtered.pkl', 'rb') as file_in:
			cache = pickle.load(file_in)

		print(cache.keys())

		if query in cache and use_cache:
			return cache[query]

		tweets = []
		text_set = set()

		prev_id = -1
		for i in tqdm(range(10)):
		#for page in tweepy.Cursor(self.api.search, q=query, count=15, tweet_mode='extended').pages():
			page = self.api.search(q=query, count=1000, max_id=str(prev_id-1), tweet_mode='extended')
			time.sleep(8)
			for status in page:
					try:
						status_data = {}

						if hasattr(status, 'retweeted_status'):
							status_data['text'] = self.post_process(status.retweeted_status.full_text)
						else:
							status_data['text'] = self.post_process(status.full_text)

						if status_data['text'] not in text_set:
							text_set.add(status_data['text'])

							#print(status_data['text'])

							status_data['name'] = status.user.screen_name
							#status_data['screen_name'] = status.user.screen_name
							
							prev_id = status.id

							tweets.append(status_data)
					except tweepy.TweepError as e:
						break

		cache[query] = tweets

		with open(out_path, 'wb') as file_out:
			pickle.dump(cache, file_out)

		create_filtered()

		return tweets

	def update_cache(self):
		with open('db_filtered.pkl', 'rb') as file_in:
			cache = pickle.load(file_in)

		for q in cache.keys():
			print(q)
			self.get_tweets(q, use_cache=False)

	def generate_cache(self, out_path='db.pkl', num_topics=5):
		NY_WOE = 2459115

		trends = self.api.trends_place(NY_WOE)[0]

		trends_name = list(map(lambda x: x['name'], trends['trends']))
		print(trends_name)

		for q in trends_name[:num_topics]:
			self.get_tweets(q, use_cache=False)

	def get_test_tweets(self, in_path='test_data.pkl'):
		with open(in_path, 'rb') as file_in:
			return pickle.load(file_in)

	def gen_test_tweets(self, out_path='test_data.pkl'):
		tweets = self.get_tweets('Emmett')

		print(tweets)

		with open(out_path, 'wb') as file_out:
			pickle.dump(tweets, file_out)

if __name__ == '__main__':
	twitter = TwitterAPI()

	twitter.update_cache()