from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.views.generic import View
from django.utils.decorators import method_decorator

class Profile(View):
    def get(self, request):
        return render_to_response('dbauth/profile.html', {
            'user': request.user,
        }, context_instance=RequestContext(request))

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Profile, self).dispatch(*args, **kwargs)
