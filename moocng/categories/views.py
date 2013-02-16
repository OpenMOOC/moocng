from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from moocng.categories.models import Category


def category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)

    return render_to_response('categories/category.html', {
        'category': category,
    }, context_instance=RequestContext(request))
