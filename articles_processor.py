import re
from news_api import NewsAPI
import random
import urllib

news = NewsAPI()

def get_articles_package(keyword_list, max_time, params):
	# get raw text
	data_all = {}

	for kw in keyword_list:
		data = news.get_articles_from_query(kw, max_num=5, **params)

		print(data)

		data_all[kw] = data

	# get articles under time
	article_package = []

	curr_time = 0
	idx = 0

	min_num_articles = len(data_all[keyword_list[0]])
	for key, val in data_all.items():
		min_num_articles = min(min_num_articles, len(val))

	while curr_time < max_time:
		if idx >= min_num_articles:
			break

		for key, val in data_all.items():
			article = val[idx]

			article_package.append(article)

			if params['summary']:
				curr_time += article['summ_min']
			else:
				curr_time += article['min']
		idx += 1

	return article_package