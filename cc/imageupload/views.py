from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.context_processors import csrf

from imageupload.models import *

def upload_image(request):
    # Handle file upload
    if request.method == 'POST':
    	form = UploadImageForm(request.POST, request.FILES)
    	if form.is_valid():
	    handle_uploaded_image(request.FILES['imgfile'])
            newimg = UploadImage(title = request.POST['title'],imgfile=request.FILES['imgfile'])
	    newimg.save()

	    # Redirect to ...
            return render_to_response('message.html',{'message':'Success!'}) 
    else:
        form = UploadImageForm()
    return render_to_response('upload.html', {'form': form},
	context_instance=RequestContext(request))

def upload_image_request(request, post_obj):
    handle_uploaded_image(request.FILES['imgfile'])
    newimg = UploadImage(title = request.POST['title'],imgfile=request.FILES['imgfile'], post = post_obj)
    newimg.save()
    return newimg

def handle_uploaded_image(f):
    destination = open('media/asdf','wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()

