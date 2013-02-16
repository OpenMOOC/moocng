from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from moocng.categories.models import Category


def show_image(obj):
    try:
        return '<img src="%s" width="30" height="30" />' % obj.icon.url
    except ValueError:
        return _('This category doesn\'t have an icon')


show_image.allow_tags = True
show_image.short_description = _("Image")


class CategoryAdmin(admin.ModelAdmin):

    prepopulated_fields = {'slug': ('name', )}
    list_display = ('name', show_image, )

admin.site.register(Category, CategoryAdmin)
