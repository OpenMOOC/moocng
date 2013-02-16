from django.db import models
from django.utils.translation import ugettext_lazy as _

from moocng.courses.models import Course


class Category(models.Model):

    name = models.CharField(verbose_name=_(u'Name'), max_length=200,
                            blank=False, null=False)
    slug = models.SlugField(verbose_name=_(u'Slug'), blank=False, null=False)
    icon = models.ImageField(verbose_name=_(u'Category\'s icon'),
                             upload_to='category_icons', blank=True, null=True)
    courses = models.ManyToManyField(Course, related_name='categories',
                                     verbose_name=_(u'Courses'),
                                     blank=True, null=True)

    class Meta:
        verbose_name = _(u'category')
        verbose_name_plural = _(u'categories')

    def __unicode__(self):
        return self.name
