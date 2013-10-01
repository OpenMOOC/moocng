# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.query import QuerySet


class ExternalAppQuerySet(QuerySet):

    def by_visibility(self, visibility):
        return self.filter(visibility=visibility)

    def me(self):
        return self.by_visibility(visibility=1)

    def students(self):
        return self.by_visibility(visibility=2)


class ExternalAppManager(models.Manager):

    def get_query_set(self):
        return ExternalAppQuerySet(self.model, using=self._db)

    def me(self):
        return self.get_query_set().me()

    def students(self):
        return self.get_query_set().students()
