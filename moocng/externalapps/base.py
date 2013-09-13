# -*- coding: utf-8 -*-
from django.utils import six
from django.db.models.loading import get_model

from moocng.externalapps.exceptions import InstanceLimitReached

DEFAULT_NAMES = ('app_name', 'description', 'instances', 'model',)


class ExternalAppOption(object):
    def __init__(self, meta):
        self.meta = meta

    def contribute_to_class(self, cls, name):
        cls._meta = self
        self.original_attrs = {}
        if self.meta:
            meta_attrs = self.meta.__dict__.copy()
            for name in self.meta.__dict__:
                # Ignore any private attributes that Django doesn't care about.
                # NOTE: We can't modify a dictionary's contents while looping
                # over it, so we loop over the *original* dictionary instead.
                if name.startswith('_'):
                    del meta_attrs[name]
            for attr_name in DEFAULT_NAMES:
                if attr_name in meta_attrs:
                    setattr(self, attr_name, meta_attrs.pop(attr_name))
                    self.original_attrs[attr_name] = getattr(self, attr_name)
                elif hasattr(self.meta, attr_name):
                    setattr(self, attr_name, getattr(self.meta, attr_name))
                    self.original_attrs[attr_name] = getattr(self, attr_name)

            # instances can be either a tuple of tuples, or a single
            # tuple of two strings. Normalize it to a tuple of tuples, so that
            # calling code can uniformly expect that.
            ins = meta_attrs.pop('instances', self.instances)
            if ins and not isinstance(ins[0], (tuple, list)):
                ins = (ins,)
            self.instances = ins

            # Any leftover attributes must be invalid.
            if meta_attrs != {}:
                raise TypeError("'class Meta' got invalid attribute(s): %s" % ','.join(meta_attrs.keys()))
        del self.meta


class ExternalAppBase(type):
    """
    Metaclass for all external apps.
    """
    def __new__(cls, name, bases, attrs):
        super_new = super(ExternalAppBase, cls).__new__

        if attrs == {}:
            return super_new(cls, name, bases, attrs)

        parents = [b for b in bases if isinstance(b, ExternalAppBase) and
                not (b.__mro__ == (b, object))]
        if not parents:
            return super_new(cls, name, bases, attrs)

        module = attrs.pop('__module__')
        new_class = super_new(cls, name, bases, {'__module__': module})
        attr_meta = attrs.pop('Meta', None)
        if not attr_meta:
            meta = getattr(new_class, 'Meta', None)
        else:
            meta = attr_meta
        kwargs = {}
        new_class.add_to_class('_meta', ExternalAppOption(meta, **kwargs))

        for obj_name, obj in attrs.items():
            new_class.add_to_class(obj_name, obj)
        return new_class

    def add_to_class(cls, name, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)

    def get_instance(self, new_instance):
        model = self.get_related_model()
        app_name = self._meta.app_name
        if isinstance(new_instance, model):
            ip_address = new_instance.ip_address
            if app_name and ip_address:
                db_instances = model.objects.filter(app_name__iexact=app_name,
                    ip_address__iexact=ip_address)
                for instance in self._meta.instances:
                    db_instances = db_instances.count() + 1
                    max_instances = int(instance[2])
                    if db_instances <= max_instances:
                        return instance
        raise InstanceLimitReached

    def get_related_model(self):
        model = self._meta.model
        app_label, model_name = model.split('.')
        model = get_model(app_label=app_label, model_name=model_name)
        return model


class ExternalApp(six.with_metaclass(ExternalAppBase)):

    def __init__(self, *args, **kwargs):
        if kwargs:
            for prop in list(kwargs):
                try:
                    if isinstance(getattr(self.__class__, prop), property):
                        setattr(self, prop, kwargs.pop(prop))
                except AttributeError:
                    pass
            if kwargs:
                raise TypeError("'%s' is an invalid keyword argument for this function" % list(kwargs)[0])
        super(ExternalApp, self).__init__()

    def render(self):
        raise NotImplementedError

    def create_remote_instance(self):
        raise NotImplementedError



