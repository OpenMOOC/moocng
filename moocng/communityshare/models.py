from django.db import models
from django.core.urlresolvers import reverse
from django.utils.html import urlize, escape
from django.conf import settings

import pymongo
import re
from dateutil import tz
from datetime import date, datetime

from moocng.mongodb import get_db
from bson.objectid import ObjectId

from django.contrib.auth.models import User
from moocng.courses.models import Course
from moocng.courses.utils import is_teacher
from moocng.x_api import utils as x_api


class CommunityShareBase(object):
	def __init__(self, prefix='share'):
		self.col_prefix=prefix
		self.col_post = '%s_post' % self.col_prefix

	def get_posts(self, idsQuery, page, show_children=False):
	    postCollection = get_db().get_collection(self.col_post)
	    if not show_children:
	    	posts = postCollection.find({
	    		"$and": [
	    			{"$or": idsQuery, },
	    			{"$or": [ {"is_child": {"$exists": False} }, {"is_child": False} ] },
	    			{"$or": [ {"deleted": {"$exists": False}}, {"deleted": False} ] },
	    		]
	    	})[page:page+10].sort([("pinned", pymongo.DESCENDING), ("date", pymongo.DESCENDING)])
	    else:
	    	posts = postCollection.find({
	    		"$and": [
	    			{"$or": idsQuery, },
	    			{"$or": [ {"deleted": {"$exists": False} }, {"deleted": False} ] }
	    		]
	    	})[page:page+10].sort("date",pymongo.DESCENDING)
	    posts_list = []
	    for post in posts:
	        if len(post['children']) > 0:
	            self._process_post_children(post)
	        posts_list.append(post)

	    return self._process_post_list(posts_list)

	def search_posts(self, query, page):
	    postCollection = get_db().get_collection(self.col_post)
	    mongoQuery = {'$regex': '.*%s.*' % (query)}

	    posts = postCollection.find({'text': mongoQuery})[page:page+10].sort("date",pymongo.DESCENDING)

	    return self._process_post_list(posts)

	def insert_post(self, post):
		return get_db().get_collection(self.col_post).insert(post)

	def count_posts(self, id):
	    return get_db().get_collection(self.col_post).find({'id_user': id}).count()

	def _hashtag_to_link(self, matchobj):
	    hashtag = matchobj.group(0)
	    hashtagUrl = reverse('profile_posts_hashtag', args=[hashtag[1:]])
	    return '<a href="%s">%s</a>' % (hashtagUrl, hashtag)

	def _process_hashtags(self, text):
	    hashtagged = re.sub(r'(?:(?<=\s)|^)#(\w*[A-Za-z_]+\w*)', self._hashtag_to_link, text)
	    return hashtagged

	def _process_post(self, post, from_zone, to_zone):
	    post["date"] = datetime.strptime(post.get("date"), "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=from_zone).astimezone(to_zone).strftime('%d %b %Y').upper()
	    if("original_date" in post):
	        post["original_date"] = datetime.strptime(post.get("original_date"), "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=from_zone).astimezone(to_zone).strftime('%d %b %Y').upper()
	    post["id"] = post.pop("_id")
	    post["text"] = self._process_hashtags(post["text"])

	def _process_post_list(self, posts):
	    listPost = []
	    from_zone = tz.tzutc()
	    to_zone = tz.tzlocal()

	    for post in posts:
	        post["date"] = datetime.strptime(post.get("date"), "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=from_zone).astimezone(to_zone).strftime('%d %b %Y').upper()
	        if("original_date" in post):
	            post["original_date"] = datetime.strptime(post.get("original_date"), "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=from_zone).astimezone(to_zone).strftime('%d %b %Y').upper()
	        post["id"] = post.pop("_id")
	        post["text"] = self._process_hashtags(post["text"])
	        listPost.append(post)

	    return listPost

	def _process_post_children(self, post):
	    postCollection = get_db().get_collection(self.col_post)
	    from_zone = tz.tzutc()
	    to_zone = tz.tzlocal()
	    post['replies'] = []
	    for child in post['children']:
	        post_child = postCollection.find({'_id': child}).limit(1)[0]
	        if post_child and len(post_child['children']) > 0:
	            self._process_post_children(post_child)

	        post_child["date"] = datetime.strptime(post_child.get("date"), "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=from_zone).astimezone(to_zone).strftime('%d %b %Y').upper()
	        if("original_date" in post_child):
	            post_child["original_date"] = datetime.strptime(post_child.get("original_date"), "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=from_zone).astimezone(to_zone).strftime('%d %b %Y').upper()
	        post_child["id"] = post_child.pop("_id")
	        post_child["text"] = self._process_hashtags(post_child["text"])

	        post['replies'].append(post_child)

class Microblog(CommunityShareBase):
	def __init__(self):
		super(Microblog,self).__init__('microblog')
		self.col_user = '%s_user' % self.col_prefix

	def get_blog_user(self, id):
	    return get_db().get_collection(self.col_user).find_one({'id_user': id})

	def insert_blog_user(self, user_id, following, extra=None):
		user = {
			"id_user": user_id,
			"following": following
		}
		get_db().get_collection(self.col_user).insert(user)

		# xAPI
		if extra:
			user = User.objects.get(pk=user_id)
			course = None
			resource = {
				'type': 'microblogfollow',
				'user_id': extra['user_id']
			}
			geolocation = extra.get('geolocation')
			x_api.learnerInteracts(user, resource, course, geolocation)

	def get_num_followers(self, id):
	    return get_db().get_collection(self.col_user).find({"following": {"$eq" : id}}).count()

	def update_following_blog_user(self, id, following, extra=None):
		get_db().get_collection(self.col_user).update({"id_user": id}, {"$set": {"following": following}})

		# xAPI
		if extra:
			user = User.objects.get(pk=id)
			course = None
			resource = {
				'type': 'microblogfollow',
				'user_id': extra['user_id']
			}
			geolocation = extra.get('geolocation')
			x_api.learnerInteracts(user, resource, course, geolocation)

	def get_posts(self, case, id, user, page):
	    idsUsers=[{"id_user": id}]
	    if(case == 0 and user):
	        for following in user["following"]:
	                idsUsers.append({"id_user": following})
	    return super(Microblog,self).get_posts(idsUsers, page)

	def insert_post(self, id_user, first_name, last_name, username, avatar, postText, extra=None):
		post = {
			"id_user": id_user,
			"first_name": first_name,
			"last_name":last_name,
			"username": "@%s" % (username),
			"avatar": avatar,
			"date": datetime.utcnow().isoformat(),
			"text": urlize(escape(postText)),
			"children": [],
			"favourite": [],
			"shared": 0,
		}
		post_id = super(Microblog,self).insert_post(post)

		# xAPI
		if extra and 'course_slug' in extra:
			user = User.objects.get(pk=id_user)
			try:
				course = Course.objects.get(slug=extra['course_slug'])
			except:
				course = None
			resource = {
				'type': 'microblogpost',
				'url': 'https://%s%s#%s' % (settings.API_URI, reverse('profile_posts_byid', kwargs={'id': id_user}), post_id),
				'name': 'Microblog post',
				'description': 'This is a blog post'
			}
			geolocation = extra.get('geolocation')
			x_api.learnerSubmitsAResource(user, resource, course, geolocation)

	def save_retweet(self, post_id, user_id, username, extra=None):
		postCollection = get_db().get_collection(self.col_post)
		post = postCollection.find_one({"$and": [{"id_user":user_id},{"id_original_post":ObjectId(post_id)}]})

		if(not post):
			postCollection.update({"$or": [{"_id": ObjectId(post_id)}, {"id_original_post": ObjectId(post_id)}]}, {"$inc": {"shared":  1}}, multi=True)
			post = postCollection.find_one({"_id": ObjectId(post_id)})
			post["id_author"] = post["id_user"]
			post["id_user"] = user_id
			post["id_original_post"] = post["_id"]
			post["original_date"] = post["date"]
			post["date"] = datetime.utcnow().isoformat()
			post["shared_by"] = "@%s" % (username)
			del post["_id"]
			rtpost_id = super(Microblog,self).insert_post(post)

			# xAPI
			if extra:
				user = User.objects.get(pk=user_id)
				course = None
				resource = {
					'type': 'microblogshare',
					'url': 'https://%s%s#%s' % (settings.API_URI, reverse('profile_posts_byid', kwargs={'id': user_id}), rtpost_id),
					'name': 'Microblog post',
					'description': 'This is a blog post'
				}
				geolocation = extra.get('geolocation')
				x_api.learnerSubmitsAResource(user, resource, course, geolocation)
			return True
		else:
			return False

	def save_reply(self, post_id, user_id, first_name, last_name, username, avatar, postText, extra=None):
		postCollection = get_db().get_collection(self.col_post)
		post_orig = postCollection.find_one({"_id":ObjectId(post_id)})
		if post_orig:
			post = {
				"id_user": user_id,
				"first_name": first_name,
				"last_name": last_name,
				"username": "@%s" % (username),
				"avatar": avatar,
				"date": datetime.utcnow().isoformat(),
				"text": urlize(escape(postText)),
				"children": [],
				"favourite": [],
				"shared": 0,
				"is_child": True,
			}
			reply_id = postCollection.insert(post)
			post_orig["children"].append(reply_id)
			postCollection.update({'_id': ObjectId(post_id)}, {"$set": {"children": post_orig["children"]}})

			# xAPI
			if extra and 'course_slug' in extra:
				user = User.objects.get(pk=user_id)
				try:
					course = Course.objects.get(slug=extra['course_slug'])
				except:
					course = None
					resource = {
					'type': 'microblogreply',
					'url': 'https://%s%s#%s' % (settings.API_URI, reverse('profile_posts_byid', kwargs={'id': user_id}), reply_id),
					'name': 'Microblog post',
					'description': 'This is a blog post'
					}
					geolocation = extra.get('geolocation')
					x_api.learnerSubmitsAResource(user, resource, course, geolocation)
					return True
		else:
			return False


class Blog(CommunityShareBase):
	def __init__(self):
		super('blog')


class Forum(CommunityShareBase):
	def __init__(self):
		super(Forum,self).__init__('forum')
		self.col_category = '%s_category' % self.col_prefix

	def get_forum_category(self, slug):
		return get_db().get_collection(self.col_category).find_one({'slug': slug})

	def insert_forum_category(self, name, slug):
		category = {
			"name": name,
			"slug": slug
		}
		get_db().get_collection(self.col_category).insert(category)

	def get_posts(self, category_slug, page):
	    idsQuery=[{"category_slug": category_slug}]
	    return super(Forum,self).get_posts(idsQuery, page)

	def get_post_detail(self, post_id, user_id=None):
		postCollection = get_db().get_collection(self.col_post)
		post = postCollection.find_one({
			'$and': [
				{'_id': ObjectId(post_id)},
				{"$or": [ {"deleted": {"$exists": False} }, {"deleted": False} ] }
			]
		})
		if post:
			from_zone = tz.tzutc()
			to_zone = tz.tzlocal()
			self._process_post(post, from_zone, to_zone, user_id)
			if len(post['children']) > 0:
				self._process_post_children(post, user_id)
		return post

	def insert_post(self, category_slug, id_user, first_name, last_name, username, avatar, postTitle, postText, extra=None):
		post = {
			"category_slug": category_slug,
			"id_user": id_user,
			"first_name": first_name,
			"last_name":last_name,
			"username": username,
			"avatar": avatar,
			"date": datetime.utcnow().isoformat(),
			"title": escape(postTitle),
			"text": escape(postText),
			"children": [],
			"favourite": [],
			"votes": 0,
			"voters": [],
			"shared": 0,
		}
		post_id = super(Forum,self).insert_post(post)

		# xAPI
		if extra and 'course_slug' in extra:
			user = User.objects.get(pk=id_user)
			course = Course.objects.get(slug=extra['course_slug'])
			resource = {
				'type': 'threadpost',
				'url': "https://%s%s" % (settings.API_URI, reverse('course_forum_post', kwargs={'course_slug': extra['course_slug'], 'post_id': post_id})),
				'name': post['title'],
				'description': "This is a thread-opening forum message"
			}
			geolocation = extra.get('geolocation')
			x_api.learnerSubmitsAResource(user, resource, course, geolocation)

	def save_reply(self, category_slug, post_id, id_user, first_name, last_name, username, avatar, postText, extra=None):
		postCollection = get_db().get_collection(self.col_post)
		post_orig = postCollection.find_one({"_id":ObjectId(post_id)})
		if post_orig:
			post = {
				"category_slug": category_slug,
				"id_user": id_user,
				"first_name": first_name,
				"last_name": last_name,
				"username": username,
				"avatar": avatar,
				"date": datetime.utcnow().isoformat(),
				"text": escape(postText),
				"children": [],
				"favourite": [],
				"votes": 0,
				"voters": [],
				"shared": 0,
				"is_child": True,
			}
			reply_id = postCollection.insert(post)
			post["_id"] = reply_id
			post_orig["children"].append(reply_id)
			postCollection.update({'_id': ObjectId(post_id)}, {"$set": {"children": post_orig["children"]}})

			# xAPI
			if extra and 'course_slug' in extra:
				user = User.objects.get(pk=id_user)
				course = Course.objects.get(slug=extra['course_slug'])
				resource = {
					'type': 'threadreply',
					'url': "https://%s%s#%s" % (settings.API_URI, reverse('course_forum_post', kwargs={'course_slug': extra['course_slug'], 'post_id': post_id}), reply_id),
					'name': post_orig.get('title') or "Unnamed post",
					'description': "This is a forum message"
				}
				geolocation = extra.get('geolocation')
				x_api.learnerSubmitsAResource(user, resource, course, geolocation)

			return reply_id
		else:
			return False

	def post_vote(self, post_id, id_user, vote=1, extra=None):
		postCollection = get_db().get_collection(self.col_post)
		post = postCollection.find_one({"_id": ObjectId(post_id)})
		if post:
			user_voted = [x for x in post["voters"] if id_user == x["id_user"]]
			user_vote = 0
			for hist_vote in user_voted:
				user_vote += hist_vote["vote"]
			if user_vote != vote:
				post["votes"] = post["votes"] + vote
				post["voters"].append({"id_user": id_user, "vote": vote})
				postCollection.update({"_id": ObjectId(post_id)}, {"$set": {"votes": post["votes"], "voters": post["voters"]}})
				#Update User karma
				user = User.objects.get(pk=post["id_user"])
				profile = user.get_profile()
				profile.karma += vote
				profile.save()
				user.save()

				# xAPI
				if extra and 'course_slug' in extra:
					user = User.objects.get(pk=id_user)
					course = Course.objects.get(slug=extra['course_slug'])
					resource = {
						'type': 'threadvote',
						'url': "https://%s%s" % (settings.API_URI, reverse('course_forum_post', kwargs={'course_slug': extra['course_slug'], 'post_id': post_id})),
						'name': post.get('title') or "Unnamed post",
						'description': "This is a forum message"
					}
					geolocation = extra.get('geolocation')
					x_api.learnerSubmitsAResource(user, resource, course, geolocation)

				return post["votes"]
			else:
				return False
		else:
			return False

	def post_flag(self, post_id, id_user):
		postCollection = get_db().get_collection(self.col_post)
		post = postCollection.find_one({"_id": ObjectId(post_id)})
		if post:
			if "flaggers" in post:
				user_flagged = [x for x in post["flaggers"] if id_user == x["id_user"]]
				if user_flagged:
					return True
			else:
				post["flaggers"] = []
			post["flaggers"].append({"id_user": id_user})
			postCollection.update({"_id": ObjectId(post_id)}, {"$set": {"flaggers": post["flaggers"]}})
			return True
		else:
			return False

	def post_pin(self, post_id):
		postCollection = get_db().get_collection(self.col_post)
		post = postCollection.find_one({"_id": ObjectId(post_id)})
		if post:
			if "pinned" in post:
				pinned = not post["pinned"]
			else:
				pinned = True
			postCollection.update({"_id": ObjectId(post_id)}, {"$set": {"pinned": pinned}})
			return True
		else:
			return False

	def post_edit(self, post_id, id_user, course_slug, postText):
		postCollection = get_db().get_collection(self.col_post)

		if self._can_edit(id_user, course_slug, post_id):
			postCollection.update({"_id": ObjectId(post_id)}, {"$set": {"text": escape(postText)}})
			return True
		else:
			return False

	def post_delete(self, post_id, id_user, course_slug, avoidCascade=None):
		postCollection = get_db().get_collection(self.col_post)
		if self._can_edit(id_user, course_slug, post_id):
			if avoidCascade and len(postCollection.find({"_id": ObjectId(post_id)})[0]['children']) > 0:
				return False
			postCollection.update({"_id": ObjectId(post_id)}, {"$set": {"deleted": True}})
			return True
		else:
			return False

	def _process_post(self, post, from_zone, to_zone, id_user=None):
		post["text"] = self._process_urls(post["text"])
		super(Forum, self)._process_post(post, from_zone, to_zone)
		if id_user:
			user_voted = [x for x in post["voters"] if id_user == x["id_user"]]
			post["user_vote"] = 0
			for user_vote in user_voted:
				post["user_vote"] += user_vote["vote"]

	def _process_post_children(self, post, id_user=None):
		postCollection = get_db().get_collection(self.col_post)
		from_zone = tz.tzutc()
		to_zone = tz.tzlocal()
		post['replies'] = []
		for child in post['children']:
			try:
				post_child = postCollection.find({
					'$and': [
						{'_id': child},
						{'$or': [ {'deleted': {'$exists': False} }, {'deleted': False} ] }
					]
				}).limit(1)[0]
				if post_child and len(post_child['children']) > 0:
					self._process_post_children(post_child, id_user)

				post_child["date"] = datetime.strptime(post_child.get("date"), "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=from_zone).astimezone(to_zone).strftime('%d %b %Y').upper()
				if("original_date" in post_child):
					post_child["original_date"] = datetime.strptime(post_child.get("original_date"), "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=from_zone).astimezone(to_zone).strftime('%d %b %Y').upper()
				post_child["id"] = post_child.pop("_id")
				post_child["text"] = self._process_urls(post_child["text"])
				post_child["text"] = self._process_hashtags(post_child["text"])
				if id_user:
					user_voted = [x for x in post_child["voters"] if id_user == x["id_user"]]
					post_child["user_vote"] = 0
					for user_vote in user_voted:
						post_child["user_vote"] += user_vote["vote"]

				post['replies'].append(post_child)
			except:
				pass

	def _url_to_link(self, matchobj):
	    url = matchobj.group(0)
	    return '<a href="%s" target="_blank">%s</a>' % (url, url)

	def _process_urls(self, text):
		hashtagged = re.sub(r'(?!<a href=")https?:\/\/([a-zA-Z\d._#\-\/?]+)', self._url_to_link, text)
		return hashtagged

	def _can_edit(self, id_user, course_slug, post_id=None):
		user = User.objects.get(pk=id_user)
		course = Course.objects.get(slug=course_slug)
		can_edit = False
		if user.is_superuser or is_teacher(user, course):
			can_edit = True
		elif post_id is not None:
			postCollection = get_db().get_collection(self.col_post)
			post = postCollection.find_one({"_id": ObjectId(post_id)})
			can_edit = post["id_user"] == id_user

		return can_edit
