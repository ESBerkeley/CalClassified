from cc.swamp_logging import logit, custom_log_message

from cc.ccapp.models import *
from cc.ccapp.utils import save_fb_items_to_model

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from cc.django_facebook.api import get_facebook_graph, FacebookUserConverter

from haystack.management.commands import update_index

from urlparse import urlparse, parse_qs

import datetime

@staff_member_required
def friendslist(request):
    #try:
    graph = get_facebook_graph(request)
    facebook = FacebookUserConverter(graph)
    #groups = facebook.get_groups()
    items = facebook.get_free_for_sale()
    #print json.dumps(items, sort_keys=True, indent=4, separators=(',', ': '))
    for item in items:
        thumbnail_url = item.get('picture')
        if thumbnail_url:
            link = item.get('link')
            fb_id = parse_qs(urlparse(link).query)['fbid'][0]
 #           print(fb_id)
            picture = facebook.get_facebook_url(fb_id)
 #           print(picture)
            picture_url = picture.get('source')
 #           print(picture_url)
    #print items
    #friends = facebook.get_friends()
    #likes = facebook.get_likes()
    #store_likes = facebook.get_and_store_likes(request.user)
    #print(groups)
    #print(store_likes)
    #print(queryset)
    #context_object_name = 'my_friends_list'
    #template_name = "friendslist.html"
    #except OpenFacebookException as e:
    #    print(e)
    #except:
    #    raise Http404
    update_index.Command().handle(using='default', remove=True)
    return render_to_response('friendslist.html',{'items':items},
        context_instance=RequestContext(request))

"""
@staff_member_required
def fb_items(request):
    ''
    existing_items = []
    new_items = []
    data = {}
    if request.method == 'POST':
        if request.user.is_authenticated():
            existing_items = FacebookPost.objects.all()
            try:
                graph = get_facebook_graph(request)
                facebook = FacebookUserConverter(graph)
                ffs_items = facebook.get_free_for_sale()
                txtbook_items = facebook.get_textbook_exchange()
            except:
                data['title'] = 'Relogin to Facebook'
                data['message'] = 'Your login has expired. Relogin ya doof.'
                return render_to_response('message.html', data, context_instance=RequestContext(request))
            items = ffs_items + txtbook_items
            owner, created = User.objects.get_or_create(
                first_name='Facebook',
                last_name='Bot',
                email='noreply@buynear.me',
                username='noreply@buynear.me')
            category, created = Category.objects.get_or_create(name='Facebook Post')
            for item in items:
                try:
                    item_id = item.get('id').split('_')[1]
                    item_exists = existing_items.filter(facebook_id=item_id).exists()
                except:
                    continue
                if not item_exists:
                    user_id = item.get('from').get('id')
                    seller_name = item.get('from').get('name')
                    post_url = item.get('actions')[0].get('link')
                    thumbnail_url = item.get('picture')
                    picture_url = None
                    if thumbnail_url:
                        try:
                            link = item.get('link')
                            fb_id = parse_qs(urlparse(link).query)['fbid'][0]
                            picture = facebook.get_facebook_url(fb_id)
                            picture_url = picture.get('source')
                        except:
                            pass
                    body = item.get('message')
                    if not body:
                        continue
                    price = 0
                    price_string = body.split('$')
                    if len(price_string)>1:
                        try:
                            price = (float)(re.findall(r"[-+]?\d*\.\d+|\d+", price_string[1])[0])
                        except IndexError:
                            pass
                    title = body[:48] + (body[50:] and '..')

                    created_time_string = item.get('created_time')
                    created_time = None
                    if created_time_string:
                        created_time = datetime.datetime.strptime(
                            item['created_time'], "%Y-%m-%dT%H:%M:%S+0000")
                    try:
                        new_item = FacebookPost(facebook_id=item_id,
                                        user_id=user_id,
                                        seller_name=seller_name,
                                        post_url=post_url,
                                        thumbnail_url=thumbnail_url,
                                        picture_url=picture_url,
                                        body=body,
                                        price=price,
                                        title=title,
                                        owner=owner,
                                        category=category,
                                        approved=False,
                                        created_time=created_time)
                        new_item.save()
                        new_items.append(new_item)
                    except:
                        connection._rollback()
            circle = Circle.objects.get(name='Berkeley')
            circle.itemforsale_set.add(*new_items)

            data['existing_items'] = existing_items
            data['new_items'] = new_items
            data['items'] = items
            return redirect('/fb_admin')
    else:
        if request.user.is_authenticated():
            try:
                graph = get_facebook_graph(request)
                facebook = FacebookUserConverter(graph)
                new_items = facebook.get_free_for_sale()
            except:
                pass
        existing_items = FacebookPost.objects.all()
        data['existing_items'] = existing_items
        data['new_items'] = new_items
        return render_to_response('fb_items.html', data, context_instance=RequestContext(request))
"""

@staff_member_required
def fb_to_excel(request):
    data = {}
    ffs_items = txtbook_items = clothes_items = []
    choices = ''
    limit = 1000
    existing = ''
    new_items = []
    import time
    until = datetime.datetime.utcnow()
    until = time.mktime(until.timetuple())
    since = 0
    if 'choices' in request.GET:
        choices = request.GET['choices']
    if 'limit' in request.GET:
        limit = int(request.GET['limit'])
    if 'existing' in request.GET:
        existing = request.GET['existing']
    if 'until' in request.GET:
        until = request.GET['until']
    if 'since' in request.GET:
        since = request.GET['since']
    if not existing:
        try:
            graph = get_facebook_graph(request)
            facebook = FacebookUserConverter(graph)
            if not choices or 'ffs' in choices:
                ffs_items = facebook.get_free_for_sale(limit=limit)
            if not choices or 'txt' in choices:
                txtbook_items = facebook.get_textbook_exchange(limit=limit)
            if not choices or 'cls' in choices:
                clothes_items = facebook.get_facebook_data('429395210488691/feed', limit=limit)
        except:
            data['title'] = 'Relogin to Facebook'
            data['message'] = 'Your login has expired. Relogin ya doof.'
            return render_to_response('message.html', data, context_instance=RequestContext(request))
        items = ffs_items + txtbook_items + clothes_items
        new_items = save_fb_items_to_model(facebook, items)

    existing_items = FacebookPostForExcel.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="FB-items.csv"'

    import cc.unicodecsv as csv
    writer = csv.writer(response)
    '''
    message=message,
    user_id=user_id,
    facebook_id=item_id,
    seller_name=seller_name,
    post_url=post_url,
    thumbnail_url=thumbnail_url,
    picture_url=picture_url,
    price=price,
    created_time=created_time
    '''
    writer.writerow(['Created_Time', 'Message', 'Post Url', 'Seller Name', 'Picture Url', 'Price', 'Comments', 'Likes'])
    db_items = new_items
    if existing:
        db_items = existing_items
    for item in db_items:
        try:
            updated_time = item.updated_time.isoformat()
        except:
            updated_time = "None"
        writer.writerow([updated_time,
                         item.message,
                         item.post_url,
                         item.seller_name,
                         item.picture_url,
                         str(item.price),
                         item.num_comments,
                         item.num_likes])
    return response

"""
@login_required
def fb_admin(request):
    data = {}
    if request.method == 'GET':
        formset = FacebookFormSet(queryset=FacebookPost.objects.filter(approved=False))
        last_week = datetime.datetime.now()-datetime.timedelta(weeks=-1)
        old_items = FacebookPost.objects.filter(created_time__gte=last_week)
        data['formset'] = formset
        data['old_items'] = old_items
        return render_to_response('fb_admin.html', data, context_instance=RequestContext(request))
    else:
        formset = FacebookFormSet(request.POST, queryset=FacebookPost.objects.filter(approved=False))
        if formset.is_valid():
            items = formset.save()
        last_week = datetime.datetime.now()-datetime.timedelta(days=-4)
        old_items = FacebookPost.objects.filter(created_time__gte=last_week)
        old_items.delete()
        data['approved_items'] = items
        update_index.Command().handle(using='default', remove=True)
        return render_to_response('fb_admin.html', data, context_instance=RequestContext(request))
"""

@login_required
@logit
def fb_import(request):
    if request.method == 'GET':
        existing_groups = []
        new_groups = []
        data = {}
        if request.user.is_authenticated():
            user_profile = request.user.get_profile()
            my_circles = user_profile.my_circles.all()
            my_circles_id = [o.id for o in my_circles]
            try:
                graph = get_facebook_graph(request)
                facebook = FacebookUserConverter(graph)
                groups = facebook.get_groups()
                #friends = facebook.get_friends()
                groups = sorted(groups, key=lambda group: group['bookmark_order'])
                for group in groups:
                    try:
                        existing = Circle.objects.get(fb_id=group['id'])
                        if existing not in my_circles:
                            existing_groups.append(existing)
                    except:
                        new_groups.append(group)
            except:
                existing_groups = Circle.objects.filter(is_public=True).exclude(id__in=my_circles_id).order_by('?')[:5]

            if not existing_groups:
                existing_groups = Circle.objects.filter(is_public=True).exclude(id__in=my_circles_id).order_by('?')[:5]

            data['existing_groups'] = existing_groups
            data['new_groups'] = new_groups


            user_profile.first_time = False
            user_profile.save()
            return render_to_response('fb_import.html', data, context_instance=RequestContext(request))
    else:
        user_profile = request.user.get_profile()
        create_groups = request.POST.getlist("createFbId")
        create_groups = map(int,create_groups)
        join_groups = request.POST.getlist("joinGroupId")

        graph = get_facebook_graph(request)
        facebook = FacebookUserConverter(graph)
        groups = facebook.get_groups()

        for group in groups:
            #print(group['id'])
            if not Circle.objects.filter(fb_id=group['id']) and int(group['id']) in create_groups:
                name = group['name'][:100] #this 100 comes from the circle name model max length
                circle = Circle.objects.create(name=group['name'], creator=request.user, fb_id=group['id'], url_key=Circle.make_key(),is_public=True)
                user_profile.my_circles.add(circle)

        for group_id in join_groups:
            group = Circle.objects.get(id=group_id)
            user_profile.my_circles.add(group)

        return redirect('/accounts/profile/groups/?msg=Groups have been successfully updated!')


"""@login_required
def friends(request):
    if request.user.is_authenticated():
        user = request.user
        user_profile = user.get_profile()
        if request.method == 'POST':
            form = friendsForm(request.POST)
            if form.is_valid():
                model = form.save(commit=False)
                send
        else:
            form = friendsForm()
            ecks = {'form':form}
            ecks.update(csrf(request))
            return render_to_response('friends.html',ecks, context_instance=RequestContext(request))"""