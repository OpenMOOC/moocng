import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.views import render_flatpage
from django.contrib.sites.models import get_current_site
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponseBadRequest, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import get_language
from django.utils.translation import ugettext as _

from moocng.courses.security import (get_courses_available_for_user,
									get_courses_user_is_enrolled,
									get_course_progress_for_user)
from moocng.courses.utils import (is_teacher as is_teacher_test)
from moocng.badges.utils import (get_user_badges_group_by_course)

from moocng.slug import unique_slugify
from moocng.utils import use_cache
from moocng.profile.forms import (PostForm)
from moocng.mongodb import get_db
from moocng.portal.templatetags.gravatar import (gravatar_for_email)
from moocng.communityshare.models import Microblog
import pymongo
import json
from bson import json_util
from dateutil import tz
from datetime import date, datetime
from moocng.profile.utils import (get_user)
from cgi import escape
from django.utils.html import urlize
import hashlib

def profile_timeline(request):
	return render_to_response('profile/timeline.html', {
		'profile': {},
		'request': request
		}, context_instance=RequestContext(request))

def profile_groups(request):
	return render_to_response('profile/groups.html', {
		'profile': {},
		'request': request
		}, context_instance=RequestContext(request))

# @login_required
def profile_courses(request, id, byid=False):

	if(not id):
		if(not request.user.id):
			return HttpResponseRedirect("/auth/login")
		user = request.user
		id = request.user.id
	else:
		if byid:
			user = User.objects.get(pk=id)
		else:
			user = User.objects.get(username=id)
			id = user.id

	case = _getCase(request,id)

	courses = get_courses_user_is_enrolled(user)
	courses_completed = 0
	for course in courses:
		if request.user.is_authenticated():
			course.is_enrolled = course.students.filter(id=user.id).exists()
			course.is_teacher = is_teacher_test(user, course)
			course.progress = get_course_progress_for_user(course, user)
			if course.progress == 100:
				courses_completed +=1
		else:
			course.is_enrolled = False
			course.is_teacher = False

	return render_to_response('profile/courses.html', {
		"id":id,
		"case":case,
		'request': request,
		'courses': courses,
		'courses_completed': courses_completed,
		"user_view_profile": user,
		"badges_count": get_db().get_collection('badge').find({"id_user": id}).count()
		}, context_instance=RequestContext(request))

# @login_required
def profile_badges(request, id, byid=False):
	if(not id):
		if(not request.user.id):
			return HttpResponseRedirect("/auth/login")
		user = request.user
		id = request.user.id
	else:
		if byid:
			user = User.objects.get(pk=id)
		else:
			user = User.objects.get(username=id)
			id = user.id

	courses = get_user_badges_group_by_course(user)

	return render_to_response('profile/badges.html', {
		"id": id,
		'request': request,
		"user_view_profile": user,
		"badges_count": get_db().get_collection('badge').find({"id_user": id}).count(),
		"courses": courses,
		}, context_instance=RequestContext(request))

def profile_badge(request, badgeid, id=None):

	if (badgeid):
		if(not id):
			if(not request.user.id):
				return HttpResponseRedirect("/auth/login")
			user = request.user
			id = request.user.id
		else:
			user = User.objects.get(username=id)
			id = user.id

		badge = get_db().get_collection('badge').find({"id_user": id, "id_badge": int(badgeid)})[0]
		hashed_email = hashlib.sha256(user.email + settings.BADGES_HASH_SALT).hexdigest()
		badge['id'] = badge['_id']

		return render_to_response('profile/badge.html', {
			"id":id,
			'request': request,
			"user_view_profile": user,
			"badges_count": get_db().get_collection('badge').find({"id_user": id}).count(),
			"hashed_email": hashed_email,
			"badge": badge,
			"openbadges_service_url": settings.BADGES_SERVICE_URL,
			}, context_instance=RequestContext(request))
	else:
		return HttpResponseBadRequest()

@login_required
def profile_calendar(request):
	return render_to_response('profile/calendar.html', {
		'profile': {},
		'request': request,
		}, context_instance=RequestContext(request))

# @login_required
def profile_user(request, id, byid=False):

	if(not id):
		case = None
		if(not request.user.id):
			return HttpResponseRedirect('/auth/login')
		id = request.user.id
		user =  request.user
	else:
		case = _getCase(request,id)
		if byid:
			user = User.objects.get(pk=id)
		else:
			user = User.objects.get(username=id)
			id = user.id

	courses = get_courses_user_is_enrolled(user)

	return render_to_response('profile/user.html', {
		'id': id,
		'case': case,
		'badges_count': get_db().get_collection('badge').find({'id_user': id}).count(),
		'request': request,
		'courses': courses,
		'is_user': True,
		'user_view_profile': user,
		}, context_instance=RequestContext(request))

# @login_required
def profile_posts(request, id, api=False, byid=False):
	m = Microblog()
	if(not id):
		if(not request.user.id):
			return HttpResponseRedirect("/auth/login")
		id = request.user.id
		user = request.user
	else:
		if byid:
			id = int(id)
			user = User.objects.get(pk=id)
		else:
			user = User.objects.get(username=id)
			id = user.id

	if request.method == 'POST':
		form = PostForm(request.POST)
		if form.is_valid():
			if request.META.get('HTTP_CONTEXT_URL'):
				try:
					geolocation = {
						'lat': float(request.META['HTTP_CONTEXT_GEO_LAT']),
						'lon': float(request.META['HTTP_CONTEXT_GEO_LON'])
					}
				except:
					geolocation = {
						'lat': 0.0,
						'lon': 0.0
					}
				try:
					url = request.META['HTTP_CONTEXT_URL']
					result = re.search('\/course\/(?P<slug>[a-zA-Z0-9-_]+)\/', url)
					course_slug = result.group('slug')
				except:
					course_slug = None
			else:
				try:
					geolocation = {
                    	'lat': float(request.POST['context_geo_lat']),
                    	'lon': float(request.POST['context_geo_lon'])
                	}
				except:
					geolocation = {
						'lat': 0.0,
						'lon': 0.0
					}
					
				course_slug = None

			extra = {
				'geolocation': geolocation,
				'course_slug': course_slug
			}
			m.insert_post(request.user.id, request.user.first_name, request.user.last_name, request.user.username, "https:" + gravatar_for_email(request.user.email), form.cleaned_data['postText'], extra)
			return HttpResponseRedirect("/user/posts")

	else:
		case = _getCase(request,id)

		blog_user = m.get_blog_user(request.user.id)
		if(blog_user and id in blog_user["following"]):
			following = "true"
		else:
			following = "false"

		followingCount = 0
		if(request.user.id != id):
			blog_user = m.get_blog_user(id)
			if(blog_user):
				followingCount = len(blog_user["following"])
		elif(blog_user):
			followingCount = len(blog_user["following"])

		listPost = m.get_posts(case, id, blog_user, 0)

		if not api:
			return render_to_response('profile/posts.html', {
				"id":id,
				"badges_count": get_db().get_collection('badge').find({"id_user": id}).count(),
				# "email":"@" + request.user.email.split("@")[0],
				'request': request,
				'form': PostForm(),
				'totalPost': m.count_posts(id),
				'posts': listPost,
				'case': case,
				"user_view_profile": user,
				"following": following,
				"followingCount": followingCount,
				"followerCount": m.get_num_followers(id)
				}, context_instance=RequestContext(request))
		else:
			response = {
				"id": id,
				"user": '@%s' % (user.username),
				"following": following,
				"followingCount": followingCount,
				"followerCount": m.get_num_followers(id),
				"posts": listPost
			}
			return HttpResponse(json_util.dumps(response), mimetype='application/json')

def profile_posts_search(request, query, hashtag=False, api=False):
	m = Microblog()
	if(not request.user.id):
		return HttpResponseRedirect("/auth/login")
	id = request.user.id
	user = request.user

	if request.method == 'POST':
		form = PostForm(request.POST)
		if form.is_valid():
			if request.META.get('HTTP_CONTEXT_URL'):
				try:
					geolocation = {
						'lat': float(request.META['HTTP_CONTEXT_GEO_LAT']),
						'lon': float(request.META['HTTP_CONTEXT_GEO_LON'])
					}
				except:
					geolocation = {
						'lat': 0.0,
						'lon': 0.0
					}
				try:
					url = request.META['HTTP_CONTEXT_URL']
					result = re.search('\/course\/(?P<slug>[a-zA-Z0-9-_]+)\/', url)
					course_slug = result.group('slug')
				except:
					course_slug = None
			else:
				geolocation = {
                    'lat': float(request.POST['context_geo_lat']),
                    'lon': float(request.POST['context_geo_lon'])
                }
				course_slug = None

			extra = {
				'geolocation': geolocation,
				'course_slug': course_slug
			}
			m.insert_post(request.user.id, request.user.first_name, request.user.last_name, request.user.username, "https:" + gravatar_for_email(request.user.email), form.cleaned_data['postText'], extra)
			return HttpResponseRedirect("/user/posts")

	else:
		case = _getCase(request,id)

		blog_user = m.get_blog_user(request.user.id)
		if(blog_user and id in blog_user["following"]):
			following = "true"
		else:
			following = "false"

		followingCount = 0
		if(request.user.id != id):
			blog_user = m.get_blog_user(id)
			if(blog_user):
				followingCount = len(blog_user["following"])
		elif(blog_user):
			followingCount = len(blog_user["following"])

		if hashtag:
			search_query = '#%s' % (query)
		else:
			search_query = query
		listPost = m.search_posts(search_query, 0)

		if not api:
			return render_to_response('profile/posts_search.html', {
				"id":id,
				"badges": get_db().get_collection('badge').find({"id_user": id}).count(),
				# "email":"@" + request.user.email.split("@")[0],
				'request': request,
				'form': PostForm(),
				'totalPost': m.count_posts(id),
				'posts': listPost,
				'case': case,
				"user_view_profile": user,
				"following": following,
				"followingCount": followingCount,
				"followerCount": m.get_num_followers(id),
				"query": query,
				"is_hashtag": hashtag,
				}, context_instance=RequestContext(request))
		else:
			response = {
				"query": query,
				"is_hashtag": hashtag,
				"posts": listPost
			}
			return HttpResponse(json_util.dumps(response), mimetype='application/json')


# @login_required
def load_more_posts(request, page, query, search=False, hashtag=False):
	m = Microblog()
	page = int(page)
	listPost = None
	if search and query:
		if hashtag:
			query = "#%s" % (query)
		listPost = m.search_posts(query, page)
	else:
		if(not query):
			id = request.user.id
		else:
			id = int(query)
		listPost = m.get_posts(0, id, m.get_blog_user(request.user.id), page)

	return render_to_response('profile/post.html', {
			'request': request,
			'posts': listPost
			}, context_instance=RequestContext(request))

@login_required
def user_follow(request, id, follow):
	id = int(id)
	m = Microblog()
	user = m.get_blog_user(request.user.id)

	if(follow == "0"):
		try:
			geolocation = {
				'lat': float(request.META['HTTP_CONTEXT_GEO_LAT']),
				'lon': float(request.META['HTTP_CONTEXT_GEO_LON'])
			}
		except:
			geolocation = {
				'lat': 0.0,
				'lon': 0.0
			}
		extra = {
			'geolocation': geolocation,
			'user_id': id
		}

		if(user):
			if(not id in user["following"]):
				user["following"].append(id)
				m.update_following_blog_user(request.user.id, user["following"], extra)
		else:
			m.insert_blog_user(request.user.id, [id], extra)

	elif(follow == "1" and user):
		user["following"].remove(id)
		m.update_following_blog_user(request.user.id, user["following"])

	return HttpResponse("true")

@login_required
def retweet(request, id):
	m = Microblog()
	try:
		geolocation = {
			'lat': float(request.META['HTTP_CONTEXT_GEO_LAT']),
			'lon': float(request.META['HTTP_CONTEXT_GEO_LON'])
		}
	except:
		geolocation = {
			'lat': 0.0,
			'lon': 0.0
		}
	extra = {
		'geolocation': geolocation
	}
	return HttpResponse(m.save_retweet(id, request.user.id, request.user.username, extra))

@login_required
def reply(request, id):
	if request.method == 'POST':
		m = Microblog()
		form = PostForm(request.POST)
		if form.is_valid():
			if request.META.get('HTTP_CONTEXT_URL'):
				try:
					geolocation = {
						'lat': float(request.META['HTTP_CONTEXT_GEO_LAT']),
						'lon': float(request.META['HTTP_CONTEXT_GEO_LON'])
					}
				except:
					geolocation = {
						'lat': 0.0,
						'lon': 0.0
					}
				try:
					url = request.META['HTTP_CONTEXT_URL']
					result = re.search('\/course\/(?P<slug>[a-zA-Z0-9-_]+)\/', url)
					course_slug = result.group('slug')
				except:
					course_slug = None
			else:
				geolocation = {
                    'lat': float(request.POST['context_geo_lat']),
                    'lon': float(request.POST['context_geo_lon'])
                }
				course_slug = None

			extra = {
				'geolocation': geolocation,
				'course_slug': course_slug
			}
			m.save_reply(id, request.user.id, request.user.first_name, request.user.last_name, request.user.username, "https:" + gravatar_for_email(request.user.email), form.cleaned_data['postText'],extra)
			return HttpResponseRedirect("/user/posts")

def _getCase(request, id):
	if(not request.user or not request.user.id):
		return 2

	if(not id):
		return 0

	if(request.user.id != id):
		return 1
	else:
		return 0
