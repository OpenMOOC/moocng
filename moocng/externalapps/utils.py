# -*- coding: utf-8 -*-
from django.db.models import Count
from django.db.models.loading import get_model
from moocng.externalapps.exceptions import InstanceLimitReached


class BaseInstancePicker(object):

    def __init__(self, *args, **kwargs):
        external_app = kwargs.pop('external_app')
        self.external_app = external_app
        super(BaseInstancePicker, self).__init__(*args, **kwargs)

    def get_related_model(self):
        model = self.external_app._meta.model
        app_label, model_name = model.split('.')
        model = get_model(app_label=app_label, model_name=model_name)
        return model

    def get_max_instances(self):
        total_instances = 0
        for instance in self.external_app._meta.instances:
            total_instances += instance[2]
        return total_instances

    def get_max_instances_by_ip(self):
        instances = []
        for instance in self.external_app._meta.instances:
            new_instance = {'ip_address': instance[0], 'base_url': instance[1],
                'max_instances': instance[2]}
            instances.append(new_instance)
        return instances

    def get_db_instances_by_ip(self):
        model = self.get_related_model()
        instance_type = self.external_app._meta.instance_type
        queryset = model.objects.filter(instance_type=instance_type)
        db_instances_by_ip = queryset.values('ip_address').annotate(max_instances=Count('id'))
        return db_instances_by_ip

    def get_db_instances_for_ip(self, ip_address):
        model = self.get_related_model()
        instance_type = self.external_app._meta.instance_type
        queryset = model.objects.filter(instance_type=instance_type, ip_address=ip_address)
        return queryset.count()

    def get_instance(self):
        return NotImplemented()


class DefaultInstancePicker(BaseInstancePicker):

    def get_instance(self):
        available_instance = None
        model = self.get_related_model()
        instance_type = self.external_app._meta.instance_type
        db_instances = model.objects.filter(instance_type=instance_type).count()
        total_instances = self.get_max_instances()
        available = (total_instances - db_instances) > 0
        if available:
            max_instances_by_ip = self.get_max_instances_by_ip()
            for instance in max_instances_by_ip:
                ip_address = instance['ip_address']
                base_url = instance['base_url']
                max_instances = instance['max_instances']
                db_instances = self.get_db_instances_for_ip(ip_address)
                if max_instances > db_instances:
                    available_instance = (ip_address, base_url, max_instances,)
        elif not available or not available_instance:
            raise InstanceLimitReached

        return available_instance

