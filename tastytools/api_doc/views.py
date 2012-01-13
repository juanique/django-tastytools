from django.shortcuts import render_to_response
from django.template import RequestContext

def doc(request):
    return render_to_response('api_doc/doc.html',
            context_instance=RequestContext(request))

def howto(request):
    return render_to_response('api_doc/howto.html',
            context_instance=RequestContext(request))
