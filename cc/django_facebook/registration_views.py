from django.contrib.auth import authenticate, login
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, redirect
from django.template.context import RequestContext

from django_facebook.models import *
from django_facebook.utils import get_registration_backend

from ccapp.models import *
from templated_email import send_templated_mail

import random

RANDOM_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'


def register(request):
    """
    A very simplistic register view
    """
    
    """ ORIGINAL CODE
    backend = get_registration_backend()
    form_class = backend.get_form_class(request)
    template_name = backend.get_registration_template()

    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            new_user = backend.register(request, **form.cleaned_data)
            response = backend.post_registration_redirect(request, new_user)
            #keep the post behaviour exactly the same as django facebook
            
            return response
    else:
        form = form_class()
    
    context = RequestContext(request)
    context['form'] = form
    response = render_to_response(template_name, context_instance=context)
    
    return response"""

    data = {}
    if request.method == 'POST':

        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        #gender = request.POST['gender']
        password = request.POST['password']
        try:

            user = authenticate(username=email,password=password)
            if user is None:
                raise User.DoesNotExist
            if user.is_active == False: #if user has not yet activated, resend data
                user.delete()
                raise User.DoesNotExist
            data['title'] = "Registration Error"
            data['message'] = "That email exists already."
            form = FacebookProfileForm(request.POST)
            data['form'] = form
            return render_to_response('registration/registration_form.html',data,context_instance = RequestContext(request))
        except User.DoesNotExist: #errors if email doesn't exist which is good
            pass

        new_user = User()
        new_user.username = email
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.email = email
        new_user.set_password(password)
        new_user.is_active = False
        new_user.save()
        
        #new_user = authenticate( username= email, password=password)
        #login(request,new_user)
        
        auth_key = ""
        # create a 20 length random key
        for i in range(0,20):
            auth_key += random.choice(RANDOM_CHARS)
        
        verif = VerificationEmailID(user=new_user,auth_key=auth_key)
        verif.save()

        send_templated_mail(
            template_name='change_email',
            from_email='Buy Near Me <noreply@buynear.me>',
            recipient_list=[email],
            context={
                'auth_key':auth_key,
                'first_name':new_user.first_name,
                'full_name':new_user.get_full_name(),
                },
        )
        
        data['title'] = "Sign Up Verification"
        data['message'] = """Verification email has been sent.<br>Follow the instructions on the email to activate your account."""
        
        return render_to_response('message.html',data,context_instance=RequestContext(request))
        
        #return render_to_response('index.html',context_instance=RequestContext(request) )
    else:
        form = FacebookProfileForm()
    
    context = RequestContext(request)
    context['form'] = form
    response = render_to_response('registration/registration_form.html', context_instance=context)
    
    return response
    

## Creates the body for the email
#def create_body(auth_key,user):
#    site_name = Site.objects.all()[0].name
#    site_domain = Site.objects.all()[0].domain
#
#    BODY = """Greetings %s,\n\nYou (or someone pretending to be you) have asked to register an account at
#    %s.  If this wasn't you, please ignore this email
#    and your address will be removed from our records.
#
#    To activate this account, please click the following link:
#
#    http://%s/verify_user/%s\n\nSincerely,
#    %s Management""" % (user.first_name,site_name,site_domain,auth_key,site_name)
#
#    return BODY

