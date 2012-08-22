from django.forms.widgets import Widget
from django.utils.safestring import mark_safe

class ImageReadOnlyWidget(Widget):

    def render(self, name, value, attrs=None):
        return mark_safe(u'<img src="%s" />' % value.url)
