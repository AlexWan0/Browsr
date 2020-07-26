import re
from flask import Flask, render_template, request, jsonify, session, send_from_directory
from rake_nltk import Rake
from twitter_api import TwitterAPI
from news_api import NewsAPI
from textblob import TextBlob
import random
import urllib
from nltk.tag import pos_tag
from rq import Queue, Connection
from rq.job import Job
from redis import Redis
from tweet_processor import get_tweet_package
from keyword_processor import get_tags_from_text
from articles_processor import get_articles_package
import time
import os

q = Queue(connection=Redis('localhost', 6379))

app = Flask(__name__, static_folder='static')

@app.route('/favicon.ico')
def serve_favicon():
	return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/social')
def social():
	return render_template('social.html')

@app.route('/tweets')
def tweets():
	query = urllib.parse.unquote(request.args.get('query'))
	page = int(request.args.get('page'))

	maxpolar = request.args.get('maxpolar')
	source = request.args.get('source')
	if len(maxpolar) > 0:
		maxpolar = float(maxpolar)
	else:
		maxpolar = 1.0

	print('query:', query)

	job = q.enqueue_call(func=get_tweet_package, args=(query, maxpolar), result_ttl=800)

	while not job.is_finished and not job.is_failed:
		time.sleep(1)

	if job.is_finished:
		tweets = job.result

		page_size = 15

		return jsonify({'tweets': tweets[(page-1)*page_size:(page)*page_size], 'has_next': page*page_size < len(tweets)})

@app.route('/keywords', methods=['POST'])
def keywords():
	text = request.form['text']

	job = q.enqueue_call(func=get_tags_from_text, args=(text,), result_ttl=800)

	while not job.is_finished and not job.is_failed:
		time.sleep(1)

	if job.is_finished:
		return jsonify(job.result)
	return jsonify([])

@app.route('/research')
def research():
	return render_template('research.html')

@app.route('/get_articles')
def articles():
	max_time = int(request.args.get('max_time'))
	keyword_list = request.args.get('keywords').split(',')
	
	params = {'max_subjectivity': float(request.args.get('max_subjectivity')),
			'min_length': int(request.args.get('min_length')),
			'major_source_only': request.args.get('major_source_only') == 'true',
			'summary': request.args.get('summary') == 'true'}

	print(params)

	job = q.enqueue_call(func=get_articles_package, args=(keyword_list, max_time, params), result_ttl=800)

	while not job.is_finished and not job.is_failed:
		time.sleep(1)

	if job.is_finished:
		return jsonify(job.result)
	return 'failed'

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80)