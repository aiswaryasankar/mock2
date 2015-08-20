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

ALL_INTERESTS = {
'Mathematics':'http://www.todayifoundout.com/wp-content/uploads/2014/11/mathematics-symbols.jpg', 
'Biology': 'http://www.ccny.cuny.edu/biology/images/biologybanner.jpg',
'Chemistry': 'http://www.learnin4livin.com/wp-content/uploads/2014/07/acl2.jpg',
'Physics': 'http://callidolearning.com/wp-content/uploads/2015/07/physics.jpeg',
'Earth Science': 'http://science.nasa.gov/media/medialibrary/2011/03/01/small_earth.jpg',
'History': 'http://xemlasuong.org/wp-content/uploads/2015/01/ebola-virus-history.jpg',
'Computer Science Theory': 'https://upload.wikimedia.org/wikipedia/en/6/64/Theoretical_computer_science.svg', 
'Computer Programming' : 'http://static.topyaps.com/wp-content/uploads/2012/12/computer-programming.jpg',
'Law' :'http://nagps.org/wordpress/wp-content/uploads/2014/02/law.jpg',
'Business' : 'http://globe-views.com/dcim/dreams/business/business-01.jpg',
'Economics' : 'http://www.stlawu.edu/sites/default/files/page-images/1economics_1.jpg',
'Finance' : 'http://intraweb.stockton.edu/eyos/hshs/content/images/2013%20Pics/finance.jpg',
'Marketing' : 'http://2z15ag3nu0eh3p41p2jsw3l1.wpengine.netdna-cdn.com/wp-content/uploads/2015/06/Marketing1.jpg',
'Arts' : 'http://bcaarts.org/images/Paint.jpg',
'Medicine' : 'http://ufatum.com/data_images/medicine/medicine5.jpg',
'Theater' : 'http://princetonfestival.org/wp-content/uploads/2015/03/LectureConvo.jpg',
'Dance' : 'http://static.wixstatic.com/media/11c679_bd0d108824a847729f998a7d4cd903de.gif',
'Health' : 'http://www.pacific.edu/Images/administration/finance/hr/healthy-heart.jpg',
'Food' : 'http://www.changefood.org/wp-content/uploads/2013/09/feel-healthier-bodymind-fresh-food-better-than-canned_32.jpg',
'Foreign Language' : 'http://www.scps.nyu.edu/content/scps/academics/departments/foreign-languages/_jcr_content/main_content/component_carousel/image_with_overlay_1.img.jpg/1406040703759.jpg',
'Literature' : 'http://c.tadst.com/gfx/600x400/galician-literature-day-spain.jpg?1',
'Design' : 'http://www.fotosefotos.com/admin/foto_img/foto_big/vetor_em_alta_qualidade_ee11960a4ece46ad67babac86517de82_vetor%20em%20alta%20qualidade.jpg',
'Service' : 'http://www.ycdsb.ca/assets/images/christian-community-service.jpg',
'Engineering' : 'http://cdn1.tnwcdn.com/wp-content/blogs.dir/1/files/2014/03/engineering-blueprint.jpg',
'Environmental Science' : 'http://www.ccny.cuny.edu/enveng/images/essbanner.jpg',
'Speech' : 'http://trullsenglish.weebly.com/uploads/2/5/1/9/25194894/1190544_orig.jpg'
}


urlfetch.set_default_fetch_deadline(240)
secret = 'changetheworld'

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def valid_username(username):
    return username and USER_RE.match(username)

def valid_password(password):
    return password and PASS_RE.match(password)

def memcacheClub():
	#x = memcache.get('clubs')
	if x is None:
		clubQuery = Club.all()
		if clubQuery is not None:
			x = clubQuery
		else:
			x = []
	x.append(a)
	memcache.set('clubs', x)

def memcacheClublist():
	y = memcache.get('CLUB_LIST')
	if y is None:
		clubNameQuery = db.GqlQuery('Select name from Club')
		if clubNameQuery is not None:
			y = clubNameQuery
		else:
			y= []
	y.append(n)
	memcache.set('CLUB_LIST', y)

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

# def topics():
# 	x = urllib2.urlopen('https://api.coursera.org/api/catalog.v1/categories').read()
# 	j = json.loads(x)
# 	topics = []
# 	for x in range(0, len(j['elements'])):
# 		topics.append(j['elements'][x]['name'])
# 	memcache.set('topics', topics)

# def urls():
# 	start = 'http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q='
# 	urlQueries = []
# 	temp = []
# 	topics = memcache.get('topics')
# 	logging.info(topics)
# 	for a in topics:
# 		m = a.split(' ')
# 		urlQueries.append('%s%s' % (start, '%20'.join(m)))
# 	for url in urlQueries:
# 		x = urllib2.urlopen(url).read()
# 		j = json.loads(x)
# 		logging.info(j['responseData']['results'][0]['url'])
# 		temp.append( j['responseData']['results'][0]['url'])
# 	memcache.set('urls', temp)

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

	# def members (self):
	# 	return Interest.gql("where user = :n", n=self.key())

	# def render(self, num=0, int_list=[]):
	# 	return render_str("interestTable.html", int_list=int_list, num= num)

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
	def set_club_cookie(self, name='', val=''):
		cookie_hash = str(create_cookie_hash(val))
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.headers.add_header('set-cookie','club_id=%s;Path=/' % cookie_hash)
		self.response.headers['Content-Type'] = 'text/html'

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
		clubNum = self.get_cookie('club_id')
		if idNum:
			self.user = User.get_by_key_name(idNum)
		else:
			self.user=None
		if clubNum:
			self.club = Club.get_by_id(int(clubNum))
		else:
			self.club=None

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

class EditClubHandler(Handler):
	def get(self):
		# top = memcache.get('topics')
		# if top is None:
		# 	topics()
		# 	top = memcache.get('topics')
		top=ALL_INTERESTS.keys()
		club_id = self.get_cookie('club_id')
		user_id = self.get_cookie('user_id')
		if club_id and user_id:
			cl = Club.get_by_id(int(club_id))

			self.render('createClub.html', week=DAYS_OF_WEEK, topic_list= top, 
				name=cl.name, location=cl.location, time=cl.time, days=cl.days, 
				interests=cl.interests, officers=cl.officers, picUrl=cl.picUrl, 
				adviser=cl.adviser)

	def post(self):
		n = self.request.get('name')
		a = self.request.get('adviser')
		l = self.request.get('location')
		t = self.request.get('time')
		d = self.request.get_all('days')
		i = self.request.get_all('interests')
		o = self.request.get_all('officers')
		picUrl = self.request.get('picUrl')

		if self.club:
			self.club.name=n
			self.club.adviser=a
			self.club.location=l
			self.club.time=t
			self.club.days=d
			for x in self.request.get_all('interests'):
				if x not in self.club.interests:
					self.club.interests.append(x)
			self.club.officers=o
			self.club.picUrl=picUrl
			self.club.put()
		if self.get_cookie('user_id'):
			self.redirect('/clubHome/%s' % self.get_cookie('club_id'))
		

class ClubHandler(Handler):
	def get(self):
		# top = memcache.get('topics')
		# if top is None:
		# 	topics()
		# 	top = memcache.get('topics')
		top=ALL_INTERESTS.keys()
		club_id = self.get_cookie('club_id')
		user_id = self.get_cookie('user_id')
		# if club_id and user_id:
		# 	cl = Club.get_by_id(int(club_id))

		# 	self.render('createClub.html', week=DAYS_OF_WEEK, topic_list= top, 
		# 		name=cl.name, location=cl.location, time=cl.time, days=cl.days, 
		# 		interests=cl.interests, officers=cl.officers, picUrl=cl.picUrl, 
		# 		adviser=cl.adviser)
		# else:
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

		# if self.club:
		# 	self.club.name=n
		# 	self.club.adviser=a
		# 	self.club.location=l
		# 	self.club.time=t
		# 	self.club.days=d
		# 	for x in self.request.get_all('interests'):
		# 		if x not in self.club.interests:
		# 			self.club.interests.append(x)
		# 	self.club.officers=o
		# 	self.club.picUrl=picUrl
		# 	self.club.put()
		# 	logging.info(self.club.location)
		# else:
		a = Club(name=n, location=l, time=t, days=d, interests=i, officers=o, picUrl=picUrl, adviser=a)
		a.put()

		if self.get_cookie('user_id'):
			self.redirect('/clubHome/%s' % self.get_cookie('club_id'))
		elif 'Club' or 'club' in n:
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
		if not name:
			params['err_name'] = "Please enter your name."
			have_error=True
		if not idNum:
			params['err_id'] = "Please enter your id Number."
			have_error=True
		if have_error:
			self.render('signup.html', **params)
		else:
			self.register(u=username, p=password, n=name, i=idNum)
			
class InterestHandler(Handler):
	def get(self):
		if self.user:
			global ALL_INTERESTS
			# vtop = memcache.get('topics')
			# vurls = memcache.get('urls')
			# if vtop or vurls is None:
			# 	topics()
			# 	urls()
			# 	vtop = memcache.get('topics')
			# 	vurls = memcache.get('urls')
			# int_list = memcache.get('int_list')
			# l = []
			# if int_list is None:
			# 	for x in range(0, len(vtop)):
			# 		a = Interest(name=vtop[x], picUrl=vurls[x])
			# 		a.put()
			# 		l.append(a)
			# 	memcache.set('int_list', l)
			# 	int_list = memcache.get('int_list')
			# length = len(int_list)
			# self.render('interest.html', int_list = int_list, length=length)
			self.render('interest.html', ALL_INTERESTS = ALL_INTERESTS)
		else:
			self.redirect('/logout')
	
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

		CLUB_LIST= []
		clubs = Club.all()
		for x in clubs:
			CLUB_LIST.append(x.name)
		clubIds = []
		if clubs:
			for x in clubs:
				clubIds.append(str(x.key().id()))
		length = len(clubIds)
		for a in user.interests:
			m.append(a)
			w = Post.gql("where interest = :c order by created_time desc", c = a)
			for e in w:
				if e.key().id() not in postIds:
					posts.append(e)
					postIds.append(e.key().id())
		self.render('userHome.html', account=True, isClub=False, length = length, clubIds = clubIds, clubs=CLUB_LIST, user=user, posts=posts, intList=m)

	def get(self):
		if self.user:
			self.render_page(self.user)
		else:
			self.redirect('/logout')

	def post(self):
		clubName = self.request.get('club')
		clu = Club.gql('where name = :n', n=clubName).get()
		if clu:
			idNum = clu.key().id()
			logging.info('idNum = %s' %idNum)
			self.redirect('/clubHome/%s' %idNum)

class ClubHomeHandler(Handler):
	def checkOfficers(self, club):
		vari = self.get_cookie(name='user_id')
		if vari in club.officers:
			return True

	def render_page(self, post_id):
		userId = self.get_cookie('user_id')
		if userId:
			account = True
		else:
			account = False
		CLUB_LIST= []
		clubs = Club.all()
		for x in clubs:
			CLUB_LIST.append(x.name)
		club = Club.get_by_id(int(post_id))
		clubIds = []

		if clubs:
			for x in clubs:
				clubIds.append(str(x.key().id()))
		if club:
			isOfficer = self.checkOfficers(club)
			posts = Post.gql("where inputter = :c order by created_time desc", c = post_id)
			offNames = []
			for x in club.officers:
				if x != '' and User.get_by_key_name(x):
					offNames.append(User.get_by_key_name(x).name)
			self.render('clubHome.html', account = account, isClub=True, length=len(clubIds), clubIds = clubIds, clubs=CLUB_LIST, offNames = offNames, club=club, isOfficer=isOfficer, posts=posts)
		else:
			self.render('extra.html', thanks=False)

	def get(self, post_id):
		#if self.user:
		self.set_club_cookie(name='club_id', val=post_id)
		self.render_page(post_id=post_id)
		#else:
		#	self.redirect('/')

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
		self.response.headers.add_header('set-cookie', 'club_id=%s;Path=/' % var)
		self.redirect('/')

	def post(self):
		pass

class AllClubsHandler(Handler):
	def get(self):
		#clubs = memcache.get('clubs')
		clubs = Club.all()
		clubIds=[]
		if clubs:
			for x in clubs:
				clubIds.append(str(x.key().id()))
		if clubs:
			length = len(clubIds)
			self.render('allClubs.html', clubIds=clubIds, clubs= clubs, length=length)
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
    ('/editClub', EditClubHandler),
    ('/logout', LogoutHandler)
], debug=True)