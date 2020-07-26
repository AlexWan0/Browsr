import requests
from xml.etree import cElementTree as ET
from goose3 import Goose
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from textblob import TextBlob

class NewsAPI():
	def __init__(self):
		self.goose = Goose({'browser_user_agent': 'Mozilla'})

		stemmer = Stemmer('english')
		self.summarizer = Summarizer(stemmer)
		self.summarizer.stop_words = get_stop_words('english')

		self.WPM = 250

		self.MAJOR_SOURCES = set(['www.foxnews.com', 'www.cnn.com', 'www.msnbc.com', 'www.huffpost.com', 'www.nytimes.com', 'www.nbcnews.com', 'www.dailymail.co.uk', 'www.washingtonpost.com', 'www.theguardian.us', 'www.wsj.com', 'abcnews.go.com', 'www.bbc.com', 'www.bbc.co.uk', 'www.usatoday.com', 'www.latimes.com'])

	def get_subjectivity(self, text):
		blob = TextBlob(text)
		return blob.sentiment.subjectivity

	def summarize(self, text, max_sentences=8):
		parser = PlaintextParser.from_string(text, Tokenizer('english'))

		summarized = ''

		for sentence in self.summarizer(parser.document, max_sentences):
			summarized += str(sentence) + ' '

		return summarized

	def get_articles_from_query(self, query, max_num=2, max_subjectivity=0.5, min_length=30, major_source_only=True, summary=True):
		print(major_source_only)
		r = requests.get('https://news.google.com/rss/search?q='+query+'&hl=en-US&gl=US&ceid=US:en')

		data_all = []

		root = ET.fromstring(r.text)
		for i, item in enumerate(root.findall('channel/item')):
			print(len(data_all))
			try:
				if len(data_all) == max_num:
					break

				news_data = {}

				title = item.find('title').text
				url = item.find('link').text

				news_data['title'] = title
				news_data['url'] = url

				article = self.goose.extract(url=news_data['url'])

				news_data['text'] = article.cleaned_text

				news_data['summarized'] = self.summarize(news_data['text'])

				print(news_data['title'])

				# filter
				if not summary and len(news_data['text'].split(' ')) < min_length:
					print("a1")
					continue
				if summary and len(news_data['summarized'].split(' ')) < min_length:
					print("a2")
					continue
				if major_source_only and article.domain not in self.MAJOR_SOURCES:
					print("b")
					continue
				if self.get_subjectivity(news_data['text']) > max_subjectivity:
					print("c")
					continue

				if not article.top_image == None:
					news_data['image'] = article.top_image.src

				news_data['min'] = len(news_data['text'].split(' '))/self.WPM
				news_data['summ_min'] = len(news_data['summarized'].split(' '))/self.WPM

				news_data['tag'] = query

				data_all.append(news_data)
			except Exception:
				continue

		return data_all

if __name__ == '__main__':
	news = NewsAPI()

	max_time = 15
	keyword_list = ['apple', 'microsoft']
	
	params = {'max_subjectivity': 0.5,
			'min_length': 30,
			'major_source_only': True,
			'summary': True}

	# get raw text
	data_all = {}

	for kw in keyword_list:
		data = news.get_articles_from_query('apple', max_num=1, **params)

		print(data)

		data_all[kw] = data

	# get articles under time
	article_package = []

	curr_time = 0
	idx = 0

	while curr_time < max_time:
		if idx >= len(data_all[keyword_list[0]]):
			break

		for key, val in data_all.items():
			article = val[idx]

			article_package.append(article)

			if params['summary']:
				curr_time += article['summ_min']
			else:
				curr_time += article['min']
		idx += 1

	print(article_package)