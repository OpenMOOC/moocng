import importlib

from django.conf import settings
from .null import NullMediaContentHandler


def get_handler(handler_name):
    handlers = dict([(handler['id'], handler) for handler in settings.MEDIA_CONTENT_TYPES])
    handler_path = handlers.get(handler_name, {}).get('handler', None)
    if not handler_path:
        return NullMediaContentHandler()

    try:
        module_path = ".".join(handler_path.split(".")[:-1])
        class_name = handler_path.split(".")[-1]
        module = importlib.import_module(module_path)
        handler = getattr(module, class_name)()
    except Exception as e:
        print e
        raise Exception("Not valid media content handler")
    return handler
