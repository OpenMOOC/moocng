from django.utils.importlib import import_module
from django.conf import settings

__all__ = ('AuthHandler',)

module_name = ".".join(settings.AUTH_HANDLER.split(".")[0:-1])
class_name = settings.AUTH_HANDLER.split(".")[-1]
AuthHandler = getattr(import_module(module_name), class_name)
