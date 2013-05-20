from django.http import QueryDict, HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.db import models, transaction
import logging
import re
from django_facebook import settings as facebook_settings
from django.utils.encoding import iri_to_uri
from django.template.loader import render_to_string
from django_facebook.registration_backends import FacebookRegistrationBackend

# -- new DJANGO_FACEBOOK STUFF
try:
    # using compatible_datetime instead of datetime only
    # not to override the original datetime package
    from django.utils import timezone as compatible_datetime
except ImportError:
    from datetime import datetime as compatible_datetime
from functools import wraps


logger = logging.getLogger(__name__)


def clear_persistent_graph_cache(request):
    '''
    Clears the caches for the graph cache
    '''
    request.facebook = None
    request.session.delete('graph')
    if request.user.is_authenticated():
        profile = request.user.get_profile()
        profile.clear_access_token()


def test_permissions(request, scope_list, redirect_uri=None):
    '''
    Call Facebook me/permissions to see if we are allowed to do this
    '''
    from django_facebook.api import get_persistent_graph
    
    fb = get_persistent_graph(request, redirect_uri=redirect_uri)
    permissions_dict = {}
    if fb:
        #see what permissions we have
        permissions_dict = fb.permissions()

    # see if we have all permissions
    scope_allowed = True
    for permission in scope_list:
        if permission not in permissions_dict:
            scope_allowed = False

    # raise if this happens after a redirect though
    if not scope_allowed and request.GET.get('attempt'):
        raise ValueError(
              'Somehow facebook is not giving us the permissions needed, ' \
              'lets break instead of endless redirects. Fb was %s and ' \
              'permissions %s' % (fb, permissions_dict))

    return scope_allowed


def get_oauth_url(scope, redirect_uri, extra_params=None):
    '''
    Returns the oAuth URL for the given scope and redirect_uri
    '''
    scope = parse_scope(scope)
    query_dict = QueryDict('', True)
    query_dict['scope'] = ','.join(scope)
    query_dict['client_id'] = facebook_settings.FACEBOOK_APP_ID

    query_dict['redirect_uri'] = redirect_uri
    oauth_url = 'https://www.facebook.com/dialog/oauth?'
    oauth_url += query_dict.urlencode()
    return oauth_url


class CanvasRedirect(HttpResponse):
    '''
    Redirect for Facebook Canvas pages
    '''
    def __init__(self, redirect_to):
        self.redirect_to = redirect_to
        self.location = iri_to_uri(redirect_to)
        
        context = dict(location=self.location)
        js_redirect = render_to_string('django_facebook/canvas_redirect.html', context)
        
        super(CanvasRedirect, self).__init__(js_redirect)


def response_redirect(redirect_url, script_redirect=False):
    '''
    Abstract away canvas redirects
    '''
    if script_redirect:
        return ScriptRedirect(redirect_url)

    return HttpResponseRedirect(redirect_url)

def next_redirect(request, default='/', additional_params=None,
                  next_key='next', redirect_url=None, canvas=False):
    from django_facebook import settings as facebook_settings
    if facebook_settings.FACEBOOK_DEBUG_REDIRECTS:
        return HttpResponse(
            '<html><head></head><body><div>Debugging</div></body></html>')
    from django.http import HttpResponseRedirect
    if not isinstance(next_key, (list, tuple)):
        next_key = [next_key]
    
    url = request.build_absolute_uri()
    
    

    # get the redirect url
    if not redirect_url:
        for key in next_key:
            redirect_url = request.REQUEST.get(key)
            if redirect_url != None:
                next = redirect_url.split('next=')
                if len(next)>1 and next[1]:
                    redirect_url = next[1]
                    break
            if request.user.get_profile().first_time and "m." not in url:
                redirect_url = '/account_setup/'
                break
            if redirect_url and (redirect_url.startswith('/accounts/logout/') or redirect_url.startswith('/accounts/login/')):
                redirect_url = default
                break
            elif redirect_url:
                break

        if not redirect_url:

            #IF MOBILE GO ELSEWHERE (not used atm i believ)
            split_url = request.build_absolute_uri().split(".")
            if "m" in split_url or "http://m" in split_url:
                redirect_url = "/" #this is mobile redirect
            else:
                redirect_url = default #leave this here if mobile is deleted

    if additional_params:
        query_params = QueryDict('', True)
        query_params.update(additional_params)
        seperator = '&' if '?' in redirect_url else '?'
        redirect_url += seperator + query_params.urlencode()

    if canvas:
        return CanvasRedirect(redirect_url)
    
    return HttpResponseRedirect(redirect_url)


def get_profile_class():
    profile_string = settings.AUTH_PROFILE_MODULE
    app_label, model = profile_string.split('.')

    return models.get_model(app_label, model)

# BEGIN ADDED STUFF
def has_permissions(graph, scope_list):
    from open_facebook import exceptions as open_facebook_exceptions
    permissions_granted = False
    try:
        if graph:
            permissions_granted = graph.has_permissions(scope_list)
    except open_facebook_exceptions.OAuthException, e:
        pass
    return permissions_granted

def simplify_class_decorator(class_decorator):
    '''
    Makes the decorator syntax uniform
    Regardless if you call the decorator like
        @decorator
        or
        @decorator()
        or
        @decorator(staff=True)

    Complexity, Python's class based decorators are weird to say the least:
    http://www.artima.com/weblogs/viewpost.jsp?thread=240845

    This function makes sure that your decorator class always gets called with
    __init__(fn, *option_args, *option_kwargs)
    __call__()
        return a function which accepts the *args and *kwargs intended
        for fn
    '''
    # this makes sure the resulting decorator shows up as
    # function FacebookRequired instead of outer
    @wraps(class_decorator)
    def outer(fn=None, *decorator_args, **decorator_kwargs):
        # wraps isn't needed, the decorator should do the wrapping :)
        # @wraps(fn, assigned=available_attrs(fn))
        def actual_decorator(fn):
            instance = class_decorator(fn, *decorator_args, **decorator_kwargs)
            _wrapped_view = instance.__call__()
            return _wrapped_view

        if fn is not None:
            wrapped_view = actual_decorator(fn)
        else:
            wrapped_view = actual_decorator

        return wrapped_view
    return outer

# END ADDED STUFF


@transaction.commit_on_success
def mass_get_or_create(model_class, base_queryset, id_field, default_dict,
                       global_defaults):
    '''
    Updates the data by inserting all not found records
    Doesnt delete records if not in the new data

    example usage
    >>> model_class = ListItem #the class for which you are doing the insert
    >>> base_query_set = ListItem.objects.filter(user=request.user, list=1) #query for retrieving currently stored items
    >>> id_field = 'user_id' #the id field on which to check
    >>> default_dict = {'12': dict(comment='my_new_item'), '13': dict(comment='super')} #list of default values for inserts
    >>> global_defaults = dict(user=request.user, list_id=1) #global defaults
    '''
    current_instances = list(base_queryset)
    current_ids = set([unicode(getattr(c, id_field)) for c in current_instances])
    given_ids = map(unicode, default_dict.keys())
    #both ends of the comparison are in unicode ensuring the not in works
    new_ids = [g for g in given_ids if g not in current_ids]
    inserted_model_instances = []
    for new_id in new_ids:
        defaults = default_dict[new_id]
        defaults[id_field] = new_id
        defaults.update(global_defaults)
        model_instance = model_class.objects.create(
            **defaults
        )
        inserted_model_instances.append(model_instance)
    # returns a list of existing and new items
    return current_instances, inserted_model_instances


def get_form_class(backend, request):
    '''
    Will use registration form in the following order:
    1. User configured RegistrationForm
    2. backend.get_form_class(request) from django-registration 0.8
    3. RegistrationFormUniqueEmail from django-registration < 0.8
    '''
    from django_facebook import settings as facebook_settings
    form_class = None

    # try the setting
    form_class_string = facebook_settings.FACEBOOK_REGISTRATION_FORM
    if form_class_string:
        form_class = get_class_from_string(form_class_string, None)

    if not form_class:
        backend = backend or get_registration_backend()
        if backend:
            form_class = backend.get_form_class(request)
            
    assert form_class, 'we couldnt find a form class, so we cant go on like this'
            
    return form_class


def get_registration_backend():
    '''
    Ensures compatability with the new and old version of django registration
    '''
    backend = None
    backend_class = None
    
    registration_backend_string = getattr(facebook_settings, 'FACEBOOK_REGISTRATION_BACKEND', None)
    if registration_backend_string:
        backend_class = get_class_from_string(registration_backend_string)
       
    #instantiate
    if backend_class:
        backend = backend_class()
        
    return backend



def get_django_registration_version():
    '''
    Returns new, old or None depending on the version of django registration
    Old works with forms
    New works with backends
    '''
    try:
        # support for the newer implementation
        from registration.backends import get_backend
        version = 'new'
    except ImportError:
        version = 'old'
        
    try:
        import registration
    except ImportError, e:
        version = None
    
    return version


def parse_scope(scope):
    '''
    Turns
    'email,user_about_me'
    or
    ('email','user_about_me')
    into a nice consistent
    ['email','user_about_me']
    '''
    assert scope, 'scope is required'
    if isinstance(scope, basestring):
        scope_list = scope.split(',')
    elif isinstance(scope, (list, tuple)):
        scope_list = list(scope)

    return scope_list


def to_int(input, default=0, exception=(ValueError, TypeError), regexp=None):
    '''Convert the given input to an integer or return default

    When trying to convert the exceptions given in the exception parameter
    are automatically catched and the default will be returned.

    The regexp parameter allows for a regular expression to find the digits
    in a string.
    When True it will automatically match any digit in the string.
    When a (regexp) object (has a search method) is given, that will be used.
    WHen a string is given, re.compile will be run over it first

    The last group of the regexp will be used as value
    '''
    if regexp is True:
        regexp = re.compile('(\d+)')
    elif isinstance(regexp, basestring):
        regexp = re.compile(regexp)
    elif hasattr(regexp, 'search'):
        pass
    elif regexp is not None:
        raise(TypeError, 'unknown argument for regexp parameter')

    try:
        if regexp:
            match = regexp.search(input)
            if match:
                input = match.groups()[-1]
        return int(input)
    except exception:
        return default


def remove_query_param(url, key):
    p = re.compile('%s=[^=&]*&' % key, re.VERBOSE)
    url = p.sub('', url)
    p = re.compile('%s=[^=&]*' % key, re.VERBOSE)
    url = p.sub('', url)
    return url


def replace_query_param(url, key, value):
    p = re.compile('%s=[^=&]*' % key, re.VERBOSE)
    return p.sub('%s=%s' % (key, value), url)


DROP_QUERY_PARAMS = ['code', 'signed_request', 'state']

def to_bool(input, default=False):
    '''
    Take a request value and turn it into a bool
    Never raises errors
    '''
    if input is None:
        value = default
    else:
        int_value = to_int(input, default=None)
        if int_value is None:
            value = default
        else:
            value = bool(int_value)
    return value

def error_next_redirect(request, default='/', additional_params=None, next_key=None, redirect_url=None, canvas=False):
    '''
    Short cut for an error next redirect
    '''
    if not next_key:
        next_key = ['error_next', 'next']

    redirect = next_redirect(
        request, default, additional_params, next_key, redirect_url, canvas)
    return redirect

def cleanup_oauth_url(redirect_uri):
    '''
    We have to maintain order with respect to the
    queryparams which is a bit of a pain
    TODO: Very hacky will subclass QueryDict to SortedQueryDict at some point
    And use a decent sort function
    '''
    if '?' in redirect_uri:
        redirect_base, redirect_query = redirect_uri.split('?', 1)
        query_dict_items = QueryDict(redirect_query).items()
    else:
        query_dict_items = QueryDict('', True)

    # filtered_query_items = [(k, v) for k, v in query_dict_items
    #                         if k.lower() not in DROP_QUERY_PARAMS]
    # new_query_dict = QueryDict('', True)
    # new_query_dict.update(dict(filtered_query_items))

    excluded_query_items = [(k, v) for k, v in query_dict_items
                            if k.lower() in DROP_QUERY_PARAMS]
    for k, v in excluded_query_items:
        redirect_uri = remove_query_param(redirect_uri, k)

    redirect_uri = redirect_uri.strip('?')
    redirect_uri = redirect_uri.strip('&')

    return redirect_uri


def replication_safe(f):
    '''
    Usually views which do a POST will require the next page to be 
    read from the master database. (To prevent issues with replication lag).
    
    However certain views like login do not have this issue.
    They do a post, but don't modify data which you'll show on subsequent pages.
    
    This decorators marks these views as safe.
    This ensures requests on the next page are allowed to use the slave db
    '''
    from functools import wraps

    @wraps(f)
    def wrapper(request, *args, **kwargs):
        request.replication_safe = True
        response = f(request, *args, **kwargs)
        return response
    
    return wrapper

def get_class_from_string(path, default='raise'):
    """
    Return the class specified by the string.

    IE: django.contrib.auth.models.User
    Will return the user class

    If no default is provided and the class cannot be located
    (e.g., because no such module exists, or because the module does
    not contain a class of the appropriate name),
    ``django.core.exceptions.ImproperlyConfigured`` is raised.
    """
    from django.core.exceptions import ImproperlyConfigured
    backend_class = None
    try:
        from importlib import import_module
    except ImportError:
        from django.utils.importlib import import_module
    i = path.rfind('.')
    module, attr = path[:i], path[i + 1:]
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured(
            'Error loading registration backend %s: "%s"' % (module, e))
    try:
        backend_class = getattr(mod, attr)
    except AttributeError:
        if default == 'raise':
            raise ImproperlyConfigured(
                'Module "%s" does not define a registration ' \
                'backend named "%s"' % (module, attr))
        else:
            backend_class = default
    return backend_class
