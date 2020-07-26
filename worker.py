from rq import Queue, Worker, Connection
import redis

import nltk
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('stopwords')

with Connection():
	qs = ['default']

	w = Worker(qs)
	w.work()