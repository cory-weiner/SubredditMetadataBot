import praw
import re
import urllib2
from urllib2 import Request
import time
import calendar
import json

UA = 'Python/PRAW Subreddit metadata provider' # add an identifier to the user agent to trace back to you.
r = praw.Reddit(UA)
username = '' #bot username
password = '' #bot password
r.login(username,password)

def startbot():
	for c in praw.helpers.comment_stream(r,'all'):
		if check_condition(c):
			bot_action(c)

def check_condition(c):
	text = c.body
	m = re.findall('( \/?r\/\w+)',text)
	return m

def log_it(e):
	f = open('log.txt','ab')
	f.write('\n')
	f.write('---')
	f.write('\n')
	f.write(str(e))
	f.close()

def bot_action(c):
	text = c.body
	mentioned_subreddits = re.findall('( \/?r\/\w+)',text)
	target_subreddit = mentioned_subreddits[0]
	target_subreddit = target_subreddit[target_subreddit.find('r/')+2:]
	try:
		get_subreddit_data(target_subreddit,c)
	except Exception, e:
		log_it(e)
		if str(e).find('doing that too much'):
			wait = 60
			print 'waiting for ' + str(wait) + ' seconds'
			waited=0
			while waited <= wait:
				time.sleep(1)
				waited = waited + 1
				print str(waited) + ' of ' + str(wait)

def get_subreddit_data(target_subreddit,c):
	subreddit = r.get_subreddit(target_subreddit)
	if subreddit.url == c.subreddit.url:
		print 'same subreddit, moving on'
		return False
	if c.author.name == username:
		return False
	top_submission_all_time = subreddit.get_top_from_all(limit=1).next()
	top_submission_past_24_hours = subreddit.get_top(limit=1).next()
	most_controversial_submission = subreddit.get_controversial_from_all(limit=1).next()
	print 'got controversial'

	# traffic stats - adding soon

	# traffic_url = 'https://www.reddit.com%sabout/traffic/.json' % (subreddit.url)
	# traffic_data = json.load(urllib2.urlopen(Request(traffic_url,headers={'User-Agent':UA})))
	# traffic_data_clean = []
	# for record in traffic_data['month'][:3]:
	# 	month_name = calendar.month_name[time.gmtime(record[0]).tm_mon]
	# 	unique_views = record[1]
	# 	page_views = record[2]
	# 	traffic_data_clean.append({'month_name' : month_name, 'unique_views' : unique_views, 'page_views' : page_views })

	template = '''
It looks like you linked to another subreddit. I'm going to provide some metadata for {subreddit_url}. I hope you find it useful.

------

**Subscribers:** {subreddit_subscribers}

**Over 18 Only:** {subreddit_over18}

**Subreddit Type:** {subreddit_type}


&nbsp;


**Top post of all time:**

[{top_submission_score}] [{top_submission_title}]({top_submission_link}) - submitted by {top_submission_author}

**Top post past 24 hours:**

[{top_submission_24_score}] [{top_submission_24_title}]({top_submission_24_link}) - submitted by {top_submission_24_author}

**Most controversial submission:**

[{most_controversial_score}] [{most_controversial_title}]({most_controversial_link}) - submitted by {most_controversial_author}
				'''

	post_string = template.format(subreddit_url = subreddit.url.encode('ascii', 'ignore'), subreddit_subscribers = "{:,}".format(subreddit.subscribers), subreddit_over18 = subreddit.over18, subreddit_type = subreddit.subreddit_type.encode('ascii', 'ignore'), top_submission_score = "{:,}".format(top_submission_all_time.score), top_submission_title = top_submission_all_time.title.encode('ascii', 'ignore'), top_submission_author = top_submission_all_time.author.name.encode('ascii', 'ignore'), top_submission_24_score = "{:,}".format(top_submission_past_24_hours.score), top_submission_24_title = top_submission_past_24_hours.title.encode('ascii', 'ignore'), top_submission_24_author = top_submission_past_24_hours.author.name.encode('ascii', 'ignore'), most_controversial_score = "{:,}".format(most_controversial_submission.score), most_controversial_title = most_controversial_submission.title.encode('ascii', 'ignore'), most_controversial_author = most_controversial_submission.author.name.encode('ascii', 'ignore'), top_submission_link = top_submission_all_time.permalink.encode('ascii','ignore'), top_submission_24_link = top_submission_past_24_hours.permalink.encode('ascii','ignore'), most_controversial_link = most_controversial_submission.permalink.encode('ascii','ignore'))
	c.reply(post_string)

startbot()
