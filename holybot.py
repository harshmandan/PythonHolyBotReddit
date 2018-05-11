import praw
import config
import time
import pickle

holyword = "!holywater"
holydata = "holydata.gau"

def bot_login():
	print("Logging in . . .")
	r = praw.Reddit(username = config.username, password = config.password, client_id = config.client_id, client_secret = config.client_sec, user_agent = "GAU BOT Test v0.1")
	return r

def run_bot(r):
	for comment in r.subreddit('test').comments(limit = 25):
		if holyword in comment.body.lower() and comment.id not in comments_replied_to and comment.author != r.user.me() and validate_comment(comment) == True:
			print("Holyword found!")
			replycomment = prepare_comment(comment)
			try:
				print("Posting comment. . .")
				comment.reply(replycomment)
				print("Posted successfully!")
				print("Updating database . . .")
				update_moisture(comment)
				update_comments_replied_to(comment)
				print("Updated successfully!")
			except Exception as excp:
				print("Posting failed, REASON: %s" % excp)
			# Update database
			
	print ("Sleeping for 10s")
	time.sleep(10)

def validate_comment(comment):
	if get_receiver(comment) == '[deleted]':
		return False
	if get_receiver(comment) == comment.author.name.lower():
		return False
	comment.refresh()
	for child_comment in comment.replies:
		if child_comment.author.name.lower() == "gaumutrabot":
			return False
	return True


# Function to prepare comment that is to be posted

def prepare_comment(comment):
	print("Preparing comment!")
	moisture = get_moisture(comment)
	# To assign unit as the "moisture" of a user is given in L or mL (_!__ imperials)
	if moisture>=1000:
		unit = "L"
		moisture = moisture/1000
	else:
		unit = "mL"
	receiver = get_receiver(comment)
	message = "[**Here's your Holy Water, " + receiver
	message += "!**](http://i.imgur.com/x0jw93q.png \"Holy Water\") \n\n"
	message += "/u/" + receiver + " has received 50mL holy water " + "Total Holy Water is:"+ str(moisture+50) + unit
	message += comment.author.name + ") "
	print("Prepared comment is : " + message)
	return message

# Straight-up ripped function from RedditSilverBot. Sure it's ugly but it works perfectly

def get_receiver(comment):
	print("Getting receiver. . .")
	text = comment.body.lower().split()
	try:
        # Kind of gross looking code below. Splits the comment exactly once at '!RedditSilver',
        # then figures out if the very next character is a new line. If it is, respond to parent.
        # If it is not a new line, either respond to the designated person or the parent.

		split = comment.body.lower().split(holyword, 1)[1].replace(' ', '')
		if split[0] is "\n":
			try:
				receiver = comment.parent().author.name
			except AttributeError:
				receiver = '[deleted]'
		else:
			receiver = text[text.index(holyword) + 1]
    # An IndexError is thrown if the user did not specify a recipient.
	except IndexError:
		try:
			receiver = comment.parent().author.name
		except AttributeError:
			receiver = '[deleted]'
    # A ValueError is thrown if '!RedditSilver' is not found. Example: !RedditSilverTest would throw this.
	except ValueError:
		return None
	if '/u/' in receiver:
		receiver = receiver.replace('/u/', '')
	if 'u/' in receiver:
		receiver = receiver.replace('u/', '')
	if '/' in receiver:
		receiver = receiver.replace('/', '')
	print("Returning receiver:" + receiver)
	return receiver


def get_moisture(comment):
	try:
		holydata = pickle.load(open('holydata.gau', 'rb'))
	except FileNotFoundError:
		holydata = []
	if comment.author in holydata:
		moisture = holydata[comment.author]
	else:
		moisture = 0
	return moisture

def get_comments_replied_to():	
	try:
		with open("comments_replied_to.txt", "r") as f:
			comments_replied_to = f.read()
			comments_replied_to = comments_replied_to.split("\n")
			comments_replied_to = filter(None, comments_replied_to)	
	except FileNotFoundError:
		comments_replied_to = []
	return comments_replied_to

def get_holydata():
	try:
		return pickle.load(open('holydata.gau', 'rb'))
	except FileNotFoundError:
		holydata = {}
		return holydata

def update_moisture(comment):
	if comment.author in holydata:
		holydata[comment.author] += 50
	else:
		holydata[comment.author] = 50
	pickle.dump(holydata, open('holydata.gau', 'wb'))
	print("Holy data updated!")

def update_comments_replied_to(comment):
	comments_replied_to.append(comment.id)
	with open("comments_replied_to.txt", "a") as f:
				f.write(comment.id + "\n")


r = bot_login()
comments_replied_to = get_comments_replied_to()
holydata = get_holydata()
while True:
	run_bot(r)