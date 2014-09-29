from django import template

from moocng.enrollment import enrollment_methods

register = template.Library()

class BaseButtonNode(template.Node):

    def __init__(self, course):
        self.course = template.Variable(course)

    def render(self, context):
        course = self.course.resolve(context)
        enrollment_method = enrollment_methods.get(course.enrollment_method, None)
        if enrollment_method:
            return self.render_enrollment_method_button(enrollment_method, context, course)
        else:
            tpl = template.loader.get_template('enrollment/no_enrollment_method.html')
            return tpl.render(context)

    def render_enrollment_method_button(context, course):
        raise NotImplementedError()


class EnrollButtonNode(BaseButtonNode):

    def render_enrollment_method_button(self, enrollment_method, context, course):
        return enrollment_method.render_enrollment_button(context, course)


class UnenrollButtonNode(BaseButtonNode):

    def render_enrollment_method_button(self, enrollment_method, context, course):
        return enrollment_method.render_unenrollment_button(context, course)


@register.tag
def enroll_button(parser, token):
    try:
        tag_name, course = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('%r tag requires  a single argument' % token.contents.split()[0])

    return EnrollButtonNode(course)


@register.tag
def unenroll_button(parser, token):
    try:
        tag_name, course = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('%r tag requires  a single argument' % token.contents.split()[0])

    return UnenrollButtonNode(course)
