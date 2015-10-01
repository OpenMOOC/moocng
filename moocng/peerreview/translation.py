from modeltranslation.translator import translator, TranslationOptions
from moocng.peerreview.models import PeerReviewAssignment, EvaluationCriterion

class PeerReviewAssignmentTranslationOptions(TranslationOptions):
	fields = ('description',)

class EvaluationCriterionTranslationOptions(TranslationOptions):
	fields = ('title','description','description_score_1','description_score_2','description_score_3','description_score_4','description_score_5')

translator.register(PeerReviewAssignment, PeerReviewAssignmentTranslationOptions)
translator.register(EvaluationCriterion, EvaluationCriterionTranslationOptions)