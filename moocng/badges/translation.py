from modeltranslation.translator import translator, TranslationOptions
from moocng.badges.models import BadgeByCourse

class BadgeByCourseTranslationOptions(TranslationOptions):
	fields = ('title', 'description')

translator.register(BadgeByCourse, BadgeByCourseTranslationOptions)
