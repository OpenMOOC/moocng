from django.conf import settings
from django.conf.urls import patterns
from django.core.exceptions import ImproperlyConfigured
from django.utils.datastructures import SortedDict
from django.utils.importlib import import_module


class BaseEnrollment(object):
    """Base abstract for enrollment methods"""

    name = ''  # This will be stored in Course.enrollment_method
    title = ''  # Title for UI

    urls = patterns('')

    def render_enrollment_button(self):
        raise NotImplementedError()

    def render_unenrollment_button(self):
        raise NotImplementedError()


def load_enrollment_method(path):
    i = path.rfind('.')
    module, attr = path[:i], path[i+1:]
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing enrollment method %s: "%s"' % (path, e))
    except ValueError, e:
        raise ImproperlyConfigured('Error importing enrollment metehod. Is ENROLLMENT_METHODS a correctly defined list or tuple?')

    try:
        cls = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" enrollment method' % (module, attr))

    return cls()


class EnrollmentMethods(SortedDict):

    def __init__(self):
        try:
            available_method_paths = settings.ENROLLMENT_METHODS
        except AttributeError:
            available_method_paths = []

        available_methods = []
        for method in available_method_paths:
            method = load_enrollment_method(method)
            available_methods.append((method.name, method))

        super(EnrollmentMethods, self).__init__(available_methods)

    def get_choices(self):
        return [(m.name, m.title) for m in self.values()]

    def get_urlpatterns(self):
        return sum([m.urls for m in self.values()], patterns(''))

enrollment_methods = EnrollmentMethods()
