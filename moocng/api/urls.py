from django.conf.urls import include, patterns, url

from tastypie.api import Api
from moocng.api import resources

v1_api = Api(api_name='v1')
v1_api.register(resources.UnitResource())
v1_api.register(resources.KnowledgeQuantumResource())
v1_api.register(resources.AttachmentResource())
v1_api.register(resources.QuestionResource())
v1_api.register(resources.OptionResource())
v1_api.register(resources.AnswerResource())
v1_api.register(resources.ActivityResource())


urlpatterns = patterns(
    '',
    url(r'', include(v1_api.urls))
)
