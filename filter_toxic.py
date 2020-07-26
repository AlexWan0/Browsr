import nltk
nltk.download('stopwords')
nltk.download('wordnet')

import tensorflow as tf
import pickle
import re
from nltk.corpus import stopwords 
from nltk import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from tqdm import tqdm
from unidecode import unidecode
from textblob import TextBlob
from keras.preprocessing import sequence
import numpy as np

# preprocesser
stemmer = PorterStemmer()
lemmatiser = WordNetLemmatizer()
cachedStopWords = stopwords.words("english")

def process_text(text):
	result = unidecode(text)
	result = re.sub(r'(https?:\/\/)?([a-zA-Z0-9-_]{1,}\.){1,}[a-zA-Z0-9-_]{1,}(\/[A-Za-z0-9-._~:?#\[\]@!$&\'()*+,;%=]{1,}){0,}\/?', '', result)
	result = re.sub(r"'", "", result)
	result = re.sub(r"[^a-zA-Z]", " ", result)
	result = re.sub(' +', ' ', result)
	result = result.lower()
	result = ' '.join([w for w in result.split(' ') if w not in cachedStopWords])
	result = stemmer.stem(result)
	result = ' '.join([lemmatiser.lemmatize(w) for w in result.split(' ')])
	result = result.strip()
	return result

# load model
interpreter = tf.lite.Interpreter(model_path='lstm_tflite.tflite')
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

with open('lstm_token.pkl', 'rb') as file_in:
	tokenizer = pickle.load(file_in)

def classify_text(text):
	text = process_text(text)
	text = tokenizer.texts_to_sequences([text])
	text = sequence.pad_sequences(text, maxlen=128)

	interpreter.set_tensor(input_details[0]['index'], np.float32(text))

	interpreter.invoke()

	output_data = interpreter.get_tensor(output_details[0]['index'])

	return output_data[0]

def create_filtered():
	with open('db.pkl', 'rb') as file_in:
		db = pickle.load(file_in)

	db_filtered = {}

	for key, val in db.items():
		db_filtered[key] = []
		for post in tqdm(val):
			if classify_text(post['text'])[0] < 0.5:
				db_filtered[key].append(post)

	with open('db_filtered.pkl', 'wb') as file_out:
		pickle.dump(db_filtered, file_out)