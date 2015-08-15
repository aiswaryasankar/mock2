#Aiswarya Sankar
#8/5/2015

import webapp2
import jinja2
import os
import logging
import hashlib
import hmac
import re
import string
import random
import time
import math

import urllib2
import json

from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.api import memcache

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")

DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
EVENT_TYPE = ['Competition', 'Meeting notice', 'Resource', 'Reminder', 'Survey']

#clubs = []
#int_list = []
secret = 'changetheworld'

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def valid_username(username):
    return username and USER_RE.match(username)

def valid_password(password):
    return password and PASS_RE.match(password)

#password salting functions
def make_salt():
	return ''.join(random.choice(string.letters) for x in xrange(5))

def create_salt_pass(name, password, salt=''):
	if salt == '':
		salt = make_salt()
	h = str(hashlib.sha256(name+password+salt).hexdigest())
	return '%s,%s' %(salt, h)

def check_salt_pass(name, password, h):
	salt = h.split(',')[0]
	if h == create_salt_pass(name, password, salt):
		return True

#cookie hashing functions
def create_cookie_hash(val):
	return '%s|%s' %(val, hmac.new(secret, val).hexdigest())

def check_cookie_hash(h):
	val = h.split('|')[0]
	if h == create_cookie_hash(val):
		return val

def topics():
	x = urllib2.urlopen('https://api.coursera.org/api/catalog.v1/categories').read()
	j = json.loads(x)
	topics = []
	for x in range(0, len(j['elements'])):
		topics.append(j['elements'][x]['name'])
	memcache.set('topics', topics)

def urls():
	start = 'http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q='
	urlQueries = []
	temp = []
	topics = memcache.get('topics')
	for a in topics:
		m = a.split(' ')
		urlQueries.append('%s%s' % (start, '%20'.join(m)))
	for url in urlQueries:
		x = urllib2.urlopen(url).read()
		j = json.loads(x)
		temp.append( j['responseData']['results'][0]['url'])
	memcache.set('urls', temp)

########
# 4 entity kinds here User, Club, Interest and Post
########
class User(db.Model):
	name = db.StringProperty(required=True)
	username = db.StringProperty(required=True)
	idNum = db.StringProperty(required=True)
	password = db.StringProperty(required=True)
	interests = db.StringListProperty()

class Club(db.Model):
	name = db.StringProperty(required=True)
	officers = db.StringListProperty()
	interests = db.StringListProperty()
	location = db.StringProperty()
	days = db.StringListProperty()
	time = db.StringProperty() #brunch, lunch, after school
	adviser = db.StringProperty()
	picUrl = db.StringProperty()

	def render_new_post(self):
		global EVENT_TYPE
		return render_str('newPost.html', eventType = EVENT_TYPE)

class Post(db.Model):
	title = db.StringProperty()
	content = db.TextProperty()
	created_time = db.DateTimeProperty(auto_now_add = True)
	interest = db.StringListProperty() 
	inputter = db.StringProperty() 
	picUrl = db.StringProperty()
	eventType = db.StringProperty()

	def render_post(self):
		return render_str('post.html', p = self)

class Interest(db.Model):
	name = db.StringProperty()
	picUrl = db.StringProperty()

	def members (self):
		return Interest.gql("where user = :n", n=self.key())

	def render(self, num=0, int_list=[]):
		return render_str("interestTable.html", int_list=int_list, num= num)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

	def login(self, u):
		self.set_cookie(val=u.idNum)

	#cookie functions
	def set_cookie(self, name='', val=''):
		cookie_hash = str(create_cookie_hash(val))
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.headers.add_header('set-cookie','user_id=%s;Path=/' % cookie_hash)

	def get_cookie(self, name=''):
		cookie = self.request.cookies.get(name)
		if cookie:
			return check_cookie_hash(cookie)

	def initialize(self, *a, **kw):
		webapp2.RequestHandler.initialize(self, *a, **kw)
		idNum = self.get_cookie('user_id')
		if idNum:
			self.user = User.get_by_key_name(idNum)

class LoginHandler(Handler):
	def get(self):
		self.render('login.html')

	def post(self):
		username= self.request.get('username')
		password = self.request.get('password')
		u = User.gql('where username = :n', n=username).get()
		if u and check_salt_pass(username, password, u.password):
			self.login(u)
			self.redirect('/home')
		else:
			err1 = 'Please check your username.'
			self.render('login.html', err1=err1)

class ClubHandler(Handler):
	def get(self):
		top = memcache.get('topics')
		if top is None:
			topics()
			top = memcache.get('topics')
		self.render('createClub.html', week=DAYS_OF_WEEK, topic_list= top)

	def post(self):
		n = self.request.get('name')
		a = self.request.get('adviser')
		l = self.request.get('location')
		t = self.request.get('time')
		d = self.request.get_all('days')
		i = self.request.get_all('interests')
		o = self.request.get_all('officers')
		picUrl = self.request.get('picUrl')

		a = Club(name=n, location=l, time=t, days=d, interests=i, officers=o, picUrl=picUrl, adviser=a)
		a.put()

		x = memcache.get('clubs')
		if x is None:
			x = []
		x.append(a)
		memcache.set('clubs', x)
		y = memcache.get('CLUB_LIST')
		if y is None:
			y= []
		y.append(n)
		memcache.set('CLUB_LIST', y)

		if 'Club' or 'club' in n:
			self.render('extra.html', name=n, x=True, thanks=True)
		else:
			self.render('extra.html', name=n, x=False, thanks=True)

class SignUpHandler(Handler):
	def register(self, u, p, n, i):
		m = User.gql('where idNum= :n', n=i).get()
		s = User.gql('where username = :n', n = u).get()
		if m:
			self.render('signup.html', err_user = "Student id %s already has an account" %i)
		elif s:
			self.render('signup.html', err_user = "That username already exists. Please choose another.")
		else:
			password=str(create_salt_pass(u, p))
			a = User(key_name= i, username=u, password=password, name=n, idNum=i)
			a.put()
			self.set_cookie(name='user_id', val = i)
			self.redirect('/interest')

	def get(self):
		self.render('signup.html')
		
	def post(self):
		logging.info('in post')
		have_error=False
		username= self.request.get('username')
		password = self.request.get('password')
		name = self.request.get('name')
		idNum = self.request.get('idNum')

		params = dict(username = username)
		if not valid_username(username):
			params['err_user'] = "That's not a valid username."
			have_error = True
		if not valid_password(password):
			params['err_pass'] = "That's not a valid password."
			have_error = True
		if have_error:
			self.render('signup.html', **params)
		else:
			self.register(u=username, p=password, n=name, i=idNum)
			
class InterestHandler(Handler):
	def get(self):
		if self.user:
			vtop = memcache.get('topics')
			vurls = memcache.get('urls')
			if vtop or vurls is None:
				topics()
				urls()
				vtop = memcache.get('topics')
				vurls = memcache.get('urls')
			int_list = memcache.get('int_list')
			l = []
			if int_list is None:
				for x in range(0, len(vtop)):
					a = Interest(name=vtop[x], picUrl=vurls[x])
					a.put()
					l.append(a)
				memcache.set('int_list', l)
				int_list = memcache.get('int_list')
			logging.info(int_list[0])
			self.render('interest.html', int_list = int_list)
		else:
			self.redirect('/')
	
	def post(self):
		for x in self.request.get_all('interests'):
			if x not in self.user.interests:
				self.user.interests.append(x)
			else:
				logging.info(x)
		self.user.put()
		self.redirect('/home')

class HomeHandler(Handler):
	def render_page(self, user):
		m = []
		posts = []
		postIds = []
		#global CLUB_LIST
		CLUB_LIST=memcache.get('CLUB_LIST')
		#just here temporarily for testing purposes!!!
		for a in user.interests:
			m.append(a)
			w = Post.gql("where interest = :c order by created_time desc", c = a)
			for e in w:
				if e.key().id() not in postIds:
					posts.append(e)
					postIds.append(e.key().id())
		self.render('userHome.html', clubs=CLUB_LIST, user=user, posts=posts, intList=m)

	def get(self):
		if self.user:
			self.render_page(self.user)
		else:
			self.redirect('/')

	def post(self):
		clubName = self.request.get('club')
		#run query
		clu = Club.gql('where name = :n', n=clubName).get()
		if clu:
			idNum = clu.key().id()
			logging.info('idNum = %s' %idNum)
			#render appropriate page
			self.redirect('/clubHome/%s' %idNum)

class ClubHomeHandler(Handler):
	def checkOfficers(self, club):
		vari = self.get_cookie(name='user_id')
		if vari in club.officers:
			return True

	def render_page(self, post_id):
		#global CLUB_LIST
		CLUB_LIST=memcache.get('CLUB_LIST')
		club = Club.get_by_id(int(post_id))

		if club:
			isOfficer = self.checkOfficers(club)
			posts = Post.gql("where inputter = :c order by created_time desc", c = post_id)
			#for x in posts:
			#	logging.info('post content= %s' % x.content)
			offNames = []
			for x in club.officers:
				if x != '' and User.get_by_key_name(x):
					offNames.append(User.get_by_key_name(x).name)
			self.render('clubHome.html', clubs=CLUB_LIST, offNames = offNames, club=club, isOfficer=isOfficer, posts=posts)
		else:
			self.render('extra.html', thanks=False)

	def get(self, post_id):
		if self.user:
			logging.info('post_id = %s' % post_id)
			self.render_page(post_id=post_id)
		else:
			self.redirect('/')

	def post(self, post_id):
		if self.request.get('form_name') == 'search':
			clubName = self.request.get('club')
			clu = Club.gql('where name = :n', n=clubName).get()
			if clu:
				idNum = clu.key().id()
				logging.info('idNum = %s' %idNum)
				self.redirect('/clubHome/%s' %idNum)
		else:
			club = Club.get_by_id(int(post_id))
			content = self.request.get("content")
			eventType =self.request.get("eventType")
			interest = club.interests
			title = "%s posted a %s" % (club.name, eventType)
			picUrl = club.picUrl
			inputter = post_id
			p = Post(eventType=eventType, picUrl = picUrl, title=title, content=content, interest=interest, inputter=inputter)
			p.put()
			time.sleep(0.5)
			self.render_page(post_id=post_id)

class LogoutHandler(Handler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		var = ''
		self.response.headers.add_header('set-cookie', 'user_id=%s;Path=/' % var)
		self.redirect('/')

	def post(self):
		pass

class AllClubsHandler(Handler):
	def get(self):
		#global clubs
		clubs = memcache.get('clubs')
		if clubs:
			length = len(clubs) / 2 + len(clubs) % 2
			self.render('allClubs.html', clubs= clubs, length=length)
		else:
			self.response.write("No clubs have been added yet")

app = webapp2.WSGIApplication([
    ('/login', LoginHandler),
    ('/createClub', ClubHandler),
    ('/', SignUpHandler),
    ('/allClubs', AllClubsHandler),
    ('/interest', InterestHandler),
    ('/home', HomeHandler),
    ('/clubHome/(\w+)', ClubHomeHandler),
    ('/logout', LogoutHandler)
], debug=True)