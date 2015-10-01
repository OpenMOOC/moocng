from django.utils import simplejson, translation
from django.http import HttpResponse
from django.utils.html import strip_tags
import datetime
import re
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from moocng.courses.models import Course, CourseTeacher
from moocng.courses.security import (get_course_progress_for_user)
from moocng.courses.utils import (get_course_activity_dates_for_user)
from moocng.portal.templatetags.gravatar import (gravatar_for_email)
from moocng.users.models import User
from django.conf import settings
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

def ListRecords(request, num="1"):
	# courses = Course.objects.values("id", "name")
	courses = Course.objects.filter(Q(status="p") | Q(status="o"))
	# print(courses)
    # root = ElementTree.XML('<?xml version="1.0" encoding="ISO-8859-1"?><context><namespace><prefix>org.instantknowledge.com.</prefix><context>battery</context></namespace><data><state>86%</state><charging>false</charging></data></context>')
	
	# xml = dicttoxml.dicttoxml(to_json, attr_type=False, custom_root="OAI-PMH")
	root = Element('OAI-PMH')
	root.set('xmlns', 'http://www.openarchives.org/OAI/2.0/')
	root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
	root.set('xsi:schemaLocation', 'http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd')
	root.set('xmlns:lom', 'http://ltsc.ieee.org/xsd/LOM')
	root.set('xmlns:eco', 'http://www.ecolearning.eu/xsd/LOM')

	responseDate = SubElement(root, 'responseDate')
	responseDate.text = datetime.datetime.now().isoformat()

	request = SubElement(root, 'responseDate')
	request.set('verb', 'ListRecords')
	request.text = "http://streetlearn.appspot.com/oai"

	listRecords = SubElement(root, 'ListRecords')

	for course in courses:
		record = SubElement(listRecords, 'record')
		header = SubElement(record, 'header')
		if course.is_deactivated:
			header.set('status', 'deleted')
		identifier = SubElement(header, 'identifier') 
		identifier.text = '.'.join(settings.API_URI.split(".")[::-1]) + ":" + str(course.id)
		datestamp = SubElement(header, 'datestamp')   #TODO
		if course.start_date:
			datestamp.text = datetime.datetime.strptime(str(course.start_date), '%Y-%m-%d').isoformat()
		if course.owner and len(course.owner.groups.all().filter(name='teacher')) and settings.API_OFFICIAL_COURSE_TAGVALUE and course.official_course:
			setSpec = SubElement(header, 'setSpec')
			setSpec.text = settings.API_OFFICIAL_COURSE_TAGVALUE
		metadata = SubElement(record, 'metadata')
		lom = SubElement(metadata, 'lom:lom')
		general = SubElement(lom, 'lom:general')
		lidentifier = SubElement(general, 'lom:identifier')
		lcatalog = SubElement(lidentifier, 'lom:catalog')
		lcatalog.text = '.'.join(settings.API_URI.split(".")[::-1])
		lentry = SubElement(lidentifier, 'lom:entry')
		lentry.text=str(course.id)
		ltitle = SubElement(general, 'lom:title')
		
		if(len(course.languages.all()) == 0):
			lstring = SubElement(ltitle, 'lom:string')  
			lstring.set('language', 'null')
			lstring.text=course.name
		else:
			for language in course.languages.all():
				translation.trans_real.activate(language.abbr)
				lstring = SubElement(ltitle, 'lom:string')  
				lstring.set('language', language.abbr)
				lstring.text=course.name
		

		ldescription = SubElement(general, 'lom:description')
		if(len(course.languages.all()) == 0):
			lstring = SubElement(ldescription, 'lom:string')  
			lstring.set('language', 'null') 
			lstring.text = re.sub('<[^<]+?>', '', course.description)

		else:
			for language in course.languages.all():
				translation.trans_real.activate(language.abbr)
				lstring = SubElement(ldescription, 'lom:string')  
				lstring.set('language', language.abbr) 
				lstring.text = re.sub('<[^<]+?>', '', course.description)

		if(len(course.languages.all()) == 0):
			llanguage = SubElement(general, 'lom:language')
			llanguage.text = "null"
		else:
			for language in course.languages.all():
				llanguage = SubElement(general, 'lom:language')
				llanguage.text = language.abbr

		courseImage = SubElement(general, 'eco:courseImage')
		image_url = "http://" + settings.API_URI
		if course.thumbnail:
			image_url += settings.MEDIA_URL + course.thumbnail.name
		else:
			image_url += settings.STATIC_URL + 'img/classroom.jpg'

		courseImageUrl = SubElement(courseImage, 'eco:courseUrl')
		courseImageUrl.text = image_url

		units = course.unit_set.all()
		knowledgequantum = 0
		for unit in units:
			knowledgequantum += len(unit.knowledgequantum_set.all())

		nrOfUnits = SubElement(general, 'eco:nrOfUnits')
		nrOfUnits.text = str(knowledgequantum)
		estimated_effort = 2
		try:
			estimated_effort = int(course.estimated_effort)
		except:
			pass
		studyLoad = SubElement(general, 'eco:studyLoad')
		studyLoad.text = str(estimated_effort)

		startDate = SubElement(general, 'eco:startDate')
		if course.start_date:
			startDate.text = datetime.datetime.strptime(str(course.start_date), '%Y-%m-%d').isoformat()

		endDate = SubElement(general, 'eco:endDate')
		if course.end_date:
			endDate.text = datetime.datetime.strptime(str(course.end_date), '%Y-%m-%d').isoformat()
		technical = SubElement(lom, 'lom:technical')
		location = SubElement(technical, 'lom:location')
		location.text = "http://" + settings.API_URI + course.get_absolute_url()
		educational = SubElement(lom, 'lom:educational')
		typicalLearningTime = SubElement(educational, 'lom:typicalLearningTime')
		duration = SubElement(typicalLearningTime, 'lom:duration')#TODO
		if(course.start_date and course.end_date and estimated_effort):
			diff = ((course.end_date - course.start_date).days / 7) * int(estimated_effort)
			duration.text = "P"
			years = 0
			months = 0
			days = 0
			if(diff >= 8760):
				years = iff/8760
				if(years > 0):
					duration.text += str(years) + "Y"
					diff -= years * 8760
			
			if(diff >= 720):
				months = diff/720
				duration.text += str(months) + "M"
				diff -= months * 720

			if(diff >= 24):
				days = diff/24
				duration.text += str(days) + "D"
				diff -= (days * 24)

			duration.text += "T"
			if(diff != 0):
				duration.text += str(diff) + "H"

		lifeCycle = SubElement(lom, 'lom:lifeCycle')
		
		organizations = []
		for teacher in course.teachers.all():
			lcontribute = SubElement(lifeCycle, 'lom:contribute')
			lrole = SubElement(lcontribute, 'lom:role')
			lsource = SubElement(lrole, 'lom:source')
			lsource.text = "LOMv1.0"
			lvalue = SubElement(lrole, 'lom:value')
			lvalue.text = "author"
			lentity = SubElement(lcontribute, 'lom:entity')
			organization = "ECO"
			try:
				organization = teacher.get_profile().organization.all()[0].name
			except:
				pass
			if organization not in organizations:
				organizations.append(organization) 
			lentity.text="<![CDATA[BEGIN:VCARD \r\nFN:" + teacher.first_name + " " + teacher.last_name + " \r\nUID:urn:uuid:" + str(teacher.get_profile().sub) + " \r\nEMAIL;TYPE=INTERNET:" + teacher.email + " \r\nORG:" + organization + " N:" + teacher.last_name +";" + teacher.first_name + " \r\nVERSION:3.0 \r\nEND:VCARD \r\n]]>"

		for organization in organizations:
			lcontribute = SubElement(lifeCycle, 'lom:contribute')
			lrole = SubElement(lcontribute, 'lom:role')
			lsource = SubElement(lrole, 'lom:source')
			lsource.text = "LOMv1.0"
			lvalue = SubElement(lrole, 'lom:value')
			lvalue.text = "content provider"
			lentity = SubElement(lcontribute, 'lom:entity')
			lentity.text="<![CDATA[BEGIN:VCARD \r\nORG:" + organization + " \r\nVERSION:3.0 \r\nEND:VCARD \r\n]]>"
		
		lclassification = SubElement(lom, 'lom:classification')
		lpurpose = SubElement(lclassification, 'lom:purpose')
		lsource = SubElement(lpurpose, 'lom:source')
		lsource.text = "LOMv1.0"
		lvalue = SubElement(lpurpose, 'lom:value')
		lvalue.text = "discipline"
		ltaxonPath = SubElement(lclassification, 'lom:taxonPath')
		lsource = SubElement(ltaxonPath, 'lom:source')
		lstring = SubElement(lsource, 'lom:string')
		request.set('language', 'en')
		lstring.text = "ECO Area of Interests"
		ltaxon = SubElement(ltaxonPath, 'lom:taxon')
		categories = course.categories.all()
		if(len(categories) > 0):
			lid = SubElement(ltaxon, 'lom:id')
			lid.text = "ECO:" + categories[0].slug
			lentry = SubElement(ltaxon, 'lom:entry')
			lstring = SubElement(lentry, 'lom:string')
			lstring.text = categories[0].name
		
	return HttpResponse(tostring(root), mimetype='application/xml')



# from django.utils import simplejson
# from django.http import HttpResponse
# from xml.etree.ElementTree import Element, SubElement, Comment, tostring

# def prueba(request):
# 	a = "awdadawd"
#    	top = Element('top')
# 	return HttpResponse(tostring(top), mimetype='application/xml')


def courses_by_users(request,id):
	result = []
	try:
		user = User.objects.get(userprofile__sub=id)
		for coursestudent in user.coursestudent_set.all():
			course = Course.objects.get(id=coursestudent.course_id)
			current_pill = course.get_user_mark(user)
			dates_info = get_course_activity_dates_for_user(course, user)
			course_result = {
				"id": str(course.id), 
				"progressPercentage" : get_course_progress_for_user(course, user),
			}
			if "enrollDate" in dates_info:
				course_result["firstViewDate"] = dates_info["enrollDate"].isoformat()
			if "lastViewDate" in dates_info:
				course_result["lastViewDate"] = dates_info["lastViewDate"].isoformat()
			if current_pill:
				course_result["currentPill"] = current_pill.order
			result.append(course_result)
	except ObjectDoesNotExist:
		pass

	return HttpResponse(simplejson.dumps(result), mimetype='application/json')

def teacher(request,id):
	teacher = CourseTeacher.objects.filter(teacher__userprofile__sub=id)[0].teacher
	result = [{
		"name":teacher.first_name + " " + teacher.last_name, 
		"imageUrl":"http:" + gravatar_for_email(teacher.email), 
	}]
	if teacher.get_profile().language and teacher.get_profile().bio:
		result[0]["desc"] = {
			"language": teacher.get_profile().language,
			"label": strip_tags(teacher.get_profile().bio)
		}
	return HttpResponse(simplejson.dumps(result), mimetype='application/json')
	

def heartbeat(request):
    return HttpResponse(simplejson.dumps({"alive_at": datetime.datetime.now().isoformat()}), mimetype='application/json')
