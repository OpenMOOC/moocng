from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

@login_required
def profile(request):
    return render_to_response('dbauth/profile.html', {
        'user': request.user,
    }, context_instance=RequestContext(request))
