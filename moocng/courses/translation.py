from modeltranslation.translator import translator, TranslationOptions
from moocng.courses.models import Course, StaticPage, Unit, KnowledgeQuantum, Question, Option

class CourseTranslationOptions(TranslationOptions):
	fields = ('name', 'description', 'requirements', 'learning_goals', 'intended_audience', 'promotion_media_content_id')

class StaticPageTranslationOptions(TranslationOptions):
	fields = ('title', 'body')

class UnitTranslationOptions(TranslationOptions):
	fields = ('title',)

class KnowledgeQuantumTranslationOptions(TranslationOptions):
	fields = ('title', 'teacher_comments', 'supplementary_material', 'media_content_id')

class QuestionTranslationOptions(TranslationOptions):
	fields = ('solution_text',)

class OptionTranslationOptions(TranslationOptions):
	fields = ('solution', 'text', 'feedback')

translator.register(Course, CourseTranslationOptions)
translator.register(StaticPage, StaticPageTranslationOptions)
translator.register(Unit, UnitTranslationOptions)
translator.register(KnowledgeQuantum, KnowledgeQuantumTranslationOptions)
translator.register(Question, QuestionTranslationOptions)
translator.register(Option, OptionTranslationOptions)