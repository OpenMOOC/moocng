from django import template

register = template.Library()

@register.inclusion_tag('courses/usercourses.html', takes_context=True)
def usercourses(context):
    user = context['user']
    courses = user.courses_as_student.all()
    return {'courses': courses}
