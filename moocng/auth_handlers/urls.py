from django.conf.urls import include, patterns, url
from django.conf import settings
from moocng.auth_handlers import AuthHandler

urlpatterns = AuthHandler.get_urls()
