class BaseAuth(object):
    @classmethod
    def get_urls(cls):
        raise NotImplementedError()

class DBAuth(BaseAuth):
    @classmethod
    def get_urls(cls):
        from .dbauth.urls import urlpatterns
        return urlpatterns

class SAML2(BaseAuth):
    @classmethod
    def get_urls(cls):
        from .saml2.urls import urlpatterns
        return urlpatterns
