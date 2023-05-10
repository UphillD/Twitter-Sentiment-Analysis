import csv
import emoji
import re
import string
import traceback
import time


from googletrans import Translator
from textblob import TextBlob
from tqdm import tqdm

t_start = time.perf_counter()

# Initialize translator
translator = Translator()

# Initialize counter
cnt = 0
cnt_skipped = 0

# Clean tweets
def process_tweet(tweet):
	# Turn to lowercase
	tweet = tweet.lower()
	# Remove links
	url_pattern = re.compile(r'https?://\S+')
	tweet = re.sub(url_pattern, '', tweet)
	# Remove mentions
	mention_pattern = re.compile(r'@\S+')
	tweet = re.sub(mention_pattern, '', tweet)
	# Remove hashtags
	tweet = tweet.replace('#', '')
	# Demojize
	tweet = emoji.demojize(tweet, delimiters=("", ""))
	# Remove duplicate whitespaces, newlines and tabs
	tweet = tweet.replace('\n', ' ')
	tweet = tweet.replace('\t', ' ')
	tweet = tweet.replace('«', '')
	tweet = tweet.replace('»', '')
	tweet = tweet.replace('’', '')
	for c in string.punctuation:
		if c != '!':
			tweet = tweet.replace(c, '')
	for d in string.digits:
		tweet = tweet.replace(d, '')
	#tweet = tweet.replace('(', '')
	#tweet = tweet.replace(')', '')
	#tweet = tweet.replace('"', '')
	#tweet = tweet.replace(':', ''0)
	tweet = re.sub(r'\s+', ' ', tweet)
	tweet = tweet.strip()
	# Translate
	i = 5
	while i != 0:
		try:
			tweet = translator.translate(tweet, src='el', dest='en')
			tweet = tweet.text
			return(tweet)
		except KeyboardInterrupt:
			exit()
		except Exception as e:
			#traceback.print_exc()
			i -= 1

	return(None)

# Load dataset
with open('dataset.tsv', 'r') as input_tsv:
	reader = csv.reader(input_tsv, delimiter='\t')
	for row in tqdm(reader, total=288502):
		tweet = process_tweet(row[4])
		if tweet:
			cnt += 1
		else:
			cnt_skipped += 1
			continue
		blob = TextBlob(tweet)
		polarity = blob.sentiment.polarity
		subjectivity = blob.sentiment.subjectivity
		with open('dataset_output.tsv', 'a') as output_tsv:
			writer = csv.writer(output_tsv, delimiter='\t')
			writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], polarity, subjectivity])
		t_now = time.perf_counter()
		speed = cnt / (t_now - t_start)
		time_left = 288502 / speed
		measure = 'secs'
		if time_left > 60:
			time_left = time_left / 60
			measure = 'mins'
			if time_left > 60:
				time_left = time_left / 60
				measure = 'hours'


		#print('Tweets analyzed: {}, skipped: {}, speed: {:.2f} tweets/s, time remaining: {:.2f} {}'.format(cnt, cnt_skipped, speed, time_left, measure))
