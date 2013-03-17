from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from moocng.categories.models import Category


def category(request, categories):
    cat_list = []
    for cat in categories.split('/'):
        cat_list.append(get_object_or_404(Category, slug=cat))

    # intersection of the courses of all categories
    courses = cat_list[0].courses.all()
    for cat in cat_list[1:]:
        courses = [c for c in cat.courses.all() if c in courses]

    return render_to_response('categories/category.html', {
        'first_category': cat_list[0],
        'other_categories': cat_list[1:],
        'courses': courses,
    }, context_instance=RequestContext(request))
