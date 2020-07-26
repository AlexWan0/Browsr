from textblob import TextBlob
import random
import urllib
from nltk.tag import pos_tag
import re

def get_tags_from_text(text):
	text = re.sub(r"'", "", text)

	text = re.sub(r"RT", "", text)

	text = re.sub(r"@\w*", "", text)

	text = re.sub(r"[^a-zA-Z]", " ", text)

	text = re.sub(' +', ' ', text)

	print(text)

	tags_joined = []

	tags = pos_tag(text.split())

	proper_nouns = [word for word, pos in tags if pos == 'NNP']

	indices = list(map(lambda x: text.split().index(x), proper_nouns))

	print(indices)

	curr = proper_nouns.pop(0)

	prev = indices.pop(0)

	i = 0

	while len(indices) > 0:
		n = indices.pop(0)
		pn = proper_nouns.pop(0)

		if prev + 1 == n:
			curr += " " + pn
		else:
			tags_joined.append(curr)
			curr = pn

		prev = n

	tags_joined.append(curr)

	return tags_joined