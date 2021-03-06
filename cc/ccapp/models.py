from django import forms
from django.db import models
from django.core.validators import MaxLengthValidator
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.forms import ModelForm, ModelChoiceField
from django.forms.models import modelformset_factory

RANDOM_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

import random
from cc.sorl.thumbnail import get_thumbnail
from datetime import datetime, timedelta
#import sorl.thumbnail

class VerificationEmailID(models.Model):
    user = models.ForeignKey(User)
    auth_key = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)

class Post(models.Model):
    title = models.CharField(max_length=75)
    body = models.TextField(validators=[MaxLengthValidator(2000)])
    time_created = models.DateTimeField(auto_now_add=True)
    key_data = models.CharField(max_length=30, unique=True, blank=True, null=True)
    owner = models.ForeignKey(User, null=True, default=None)
    approved = models.BooleanField(default=True)
    owner_facebook_id = models.BigIntegerField(blank=True, null=True)
    expire_date = models.DateTimeField(default=datetime.now()+timedelta(days=30))

    class Meta:  #abstract base class. no actual db table
        abstract = True

    def __unicode__(self):
        return self.title

    @property
    def is_expired(self):
        if datetime.now() > self.expire_date:
            return True
        return False

class Category(models.Model):
    name = models.CharField(max_length=25)
    def __unicode__(self):
        return self.name

class Circle(models.Model):
    name = models.CharField(max_length=100) #must change along with fb_import view
    is_public = models.BooleanField(default=False)
    is_city = models.BooleanField(default=False)
    url_key = models.CharField(max_length=20,unique=True)
    creator = models.ForeignKey(User, null=True)
    description = models.TextField(null=True, blank=True)
    fb_id = models.BigIntegerField(null=True, unique=True, blank=True)
    def __unicode__(self):
        return self.name
    def get_absolute_url(self):
        return "/groups/view/%s" % self.url_key
    @staticmethod
    def make_key():
        while True:
            try:
                url_key = ""
                # create a 6 length random key
                for i in range(0,6):
                    url_key += random.choice(RANDOM_CHARS)
                c = Circle.objects.get(url_key=url_key)
            except: #circle doesn't exist with key so we good
                break
        return url_key

class CircleForm(ModelForm):

    """ #ONLY USED IF CIRCLES CAN BE PUBLIC
    circle_types = (
       (True,"Public"),
       (False,"Private"), 
    )
    
    is_public = forms.ChoiceField(required=False,
        label="Group Type",
        choices=circle_types,
        help_text="Public groups can be viewed by anyone. Private groups can only be visited by providing links.")
    """

    name = forms.CharField(label="Name", widget=forms.TextInput(attrs={'placeholder':'e.g. Berkeley'}))
    description = forms.CharField(label="Description", required=False, widget=forms.Textarea(attrs={'placeholder':'e.g. Berkeley is a city on the east shore of the San Francisco Bay in Northern California, United States. Its neighbors to the south are the cities of Oakland and Emeryville.'}))

    is_public = forms.BooleanField(widget=forms.HiddenInput(),initial=True,required=False)
    
    class Meta:
        model = Circle
        exclude = ('url_key','is_city','creator', 'fb_id')


class ItemForSale(Post): #lol extends post be sure to check its field's as well
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    category = models.ForeignKey(Category)
    circles = models.ManyToManyField(Circle)
    cached_thumb = models.CharField(max_length=200, default = '')

    num_interested_buyers = models.IntegerField(default=0)
    first_interested_buy_date = models.DateTimeField(null=True, blank=True)
    pending_buyer = models.ForeignKey(User, null=True, default=None, related_name='buyer')
    pending_flag = models.BooleanField(default=False)
    pending_date = models.DateTimeField(null=True, blank=True)
    sold = models.BooleanField(default = False)
    deleted = models.BooleanField(default = False)
    sold_date = models.DateTimeField(null=True, blank=True)

    def get_formatted_price(self):
        return "%01.2f" % self.price
    
    def get_image_set_urls(self):
        urls = []
        for image in self.image_set.order_by('id'): #.order_by('upload_date'):
            urls.append(image.image.url)
        if urls:
            return urls
        else:
            return [self.get_category_image_url()]
    
    def get_category_image_url(self):
        return '/static/images/categories/%s.png' % str(self.category).replace(',', '').lower()
    
    def get_first_image_url(self):
        try:
            return self.image_set.order_by('id')[0].image.url
        except:
            return self.get_category_image_url()
    
    def get_thumbnail_url(self):
        try:
            #if self.is_facebook_post and self.facebookpost.thumbnail_url:
                #return self.facebookpost.thumbnail_url
            if self.cached_thumb == '':
                from cc.sorl.thumbnail import get_thumbnail
                image = self.image_set.order_by('id')[0]
                im = get_thumbnail(image, "260x195", quality=75)
                self.cached_thumb = im.url
                self.save()
                return self.cached_thumb
            else:
                return self.cached_thumb
        except:
            self.cached_thumb = self.get_category_image_url()
            self.save()
            return self.cached_thumb
            
    def reset_thumbnail_url(self):
        try:
            #if self.is_facebook_post and self.facebookpost.thumbnail_url:
                #return self.facebookpost.thumbnail_url
            from cc.sorl.thumbnail import get_thumbnail
            image = self.image_set.order_by('id')[0]
            im = get_thumbnail(image, "260x195", quality=75)
            self.cached_thumb = im.url
            self.save()
            return self.cached_thumb
        except:
            self.cached_thumb = self.get_category_image_url()
            self.save()
            return self.cached_thumb
        
    def get_thumbnail_set_urls(self):
        urls = []
        from cc.sorl.thumbnail import get_thumbnail
        for image in self.image_set.order_by('id'):
#image quality
            im = get_thumbnail(image, "260x195", quality=75)
            thumb_url = im.url
            urls.append(thumb_url)
        return urls
    
    def get_seller_name(self):
        return self.owner.get_full_name()
    
    def get_seller_first_name(self):
        return self.owner.first_name
    
    def get_seller_profile_picture(self):
        return self.owner.get_profile().get_image_url()

    def is_category_image(self):
        try:
            self.image_set.order_by('id')[0].image.url
            return False
        except:
            return True
   
    @property
    def key_generate(self):
        """returns a string based unique key with length 80 chars"""
        while 1:
            import random
            key = str(random.getrandbits(66))
            try:
                ItemForSale.objects.get(key=key)
            except:
                return key
                
    def get_absolute_url(self):
        return '/%i' % self.id

    '''@property
    def is_facebook_post(self):
        try:
            self.facebookpost
            return True
        except:
            return False'''

    def delete(self): #If we're going to delete a post, let's delete its comments/images as well.
        comments = Comment.objects.filter(item = self)
        if len(comments):
            for comment in comments:
                comment.delete()
        for image in self.image_set.all():
            image.delete()
        super(ItemForSale, self).delete()


class ItemForSaleForm(ModelForm):
    """
    circles = forms.MultipleChoiceField(required=True,
        label="Groups",)
    """
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'placeholder':'e.g. Calvin and Hobbes'}))
    body = forms.CharField(label="Description",
                           help_text="Say whether it is for delivery or pickup if it is a large item.",
                           widget=forms.Textarea(
                               attrs={'placeholder':'e.g. The Tenth Anniversary Book, paperback version, 208 pages. In good condition, slightly worn cover.'}
                           ))
    category = ModelChoiceField(Category.objects.order_by('name'), empty_label="")
    class Meta:
        model = ItemForSale
        exclude = ('time_created','images', 'key_data', 'owner','owner_facebook_id','cached_thumb', 'pending_buyer',
                   'pending_date', 'pending_flag', 'sold', 'sold_date', 'deleted', 'approved','circles', 'expire_date',
                    'num_interested_buyers', 'first_interested_buy_date')

    #imgfile  = forms.ImageField(label='Select a file', help_text='max. 10 megabytes', required=False)

"""
class FacebookPost(ItemForSale):
    user_id = models.BigIntegerField(null=True)
    facebook_id = models.BigIntegerField()
    post_url = models.URLField(blank=True, null=True)
    thumbnail_url = models.URLField(blank=True, null=True)
    picture_url = models.URLField(blank=True, null=True)
    seller_name = models.TextField(blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True)

    def get_picture(self):
        if self.picture_url:
            return self.picture_url
        elif self.thumbnail_url:
            return self.thumbnail_url
        else:
            return self.get_category_image_url()

    class Meta:
        unique_together = ['user_id', 'facebook_id']

FacebookFormSet = modelformset_factory(FacebookPost, max_num=0, fields=('title','price','category', 'approved'))
"""
"""
class ClothingItem(ItemForSale):
    MALE = 'M'
    FEMALE = 'F'
    GENDER_CHOICES = (
        (MALE, 'M'),
        (FEMALE, 'F'),
    )
    XSMALL = 'XS'
    SMALL = 'S'
    MEDIUM = 'M'
    LARGE = 'L'
    XL = 'XL'
    SIZE_CHOICES = (
        (XSMALL, 'XS'),
        (SMALL, 'S'),
        (MEDIUM, 'M'),
        (LARGE, 'L'),
        (XL, 'XL')
    )
    gender = models.CharField(max_length=1,
                              choices=GENDER_CHOICES,
                              default=MALE)
    size = models.CharField(max_length=2,
                            choices=SIZE_CHOICES,
                            default=SMALL)

class ClothingItemForm(ModelForm):
    class Meta:
        model = ClothingItem
        exclude = ('approved', 'body', 'cached_thumb', 'category', 'circles', 'deleted', 'expire_date','images', 'key_data',
                   'owner','owner_facebook_id', 'pending_buyer', 'pending_flag', 'price', 'sold', 'sold_date', 'title', 'time_created')
"""
class Notification(models.Model):
    """
    TYPES:
    0 - fb friend posted 
    1 - notify the seller that someone commented
    2 - notify the commenter that the seller replied
    3 - notify the seller that someone clicked buy
    4 - notify the buyer that the seller has marked the sale complete
    5 - notify the buyer that the seller has given up on them, and reposted the item
    6 - notify the seller that the buyer has sent him a message
    7 - notify the buyer that the seller has sent him a message
    8 - notify the buyer that the seller has confirmed the purchase
    9 - notify the seller that buyer has declined to purchase
    10 - notify the seller that the buyer has reviewed their item
    11- notify the buyer that the seller has declined purchase request
    """
    going_to  = models.ForeignKey('django_facebook.FacebookProfile')
    type = models.IntegerField(default = 0)
    post_from = models.ForeignKey(ItemForSale)
    second_party = models.ForeignKey('django_facebook.FacebookProfile', blank=True, null=True, related_name='second_party')
    thread_id = models.IntegerField(default = 0)
    time_created = models.DateTimeField(auto_now_add=True, null=True)

    def __unicode__(self):
        return self.post_from.title

class Comment(models.Model):
    sender = models.ForeignKey(User)
    item = models.ForeignKey(ItemForSale, null=False, blank=False)
    body = models.CharField(max_length=200, default="", blank=False)
    seller_response = models.CharField(max_length=200, default="", blank=True)
    time_created = models.DateTimeField(auto_now_add=True, null=True)

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        exclude = ('sender','item','time_created', 'seller_response')

class SellerResponseForm(ModelForm):
    class Meta:
        model = Comment
        exclude = ('sender','item','time_created','body')


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sender_msg_set')
    recipient = models.ForeignKey(User, related_name='recipient_msg_set')
    body = models.TextField()
    #post = models.ForeignKey(ItemForSale, null=True, blank=True, related_name='responses')
    post_title = models.CharField(max_length=75, default="", blank=True)
    time_created = models.DateTimeField(auto_now_add=True,null=True)
    def __unicode__(self):
        return self.post_title

class MessageForm(ModelForm):
    class Meta:
        model = Message
        exclude = ('sender', 'recipient', 'post')
        
class Thread(models.Model):
    # owner and other_person are meant so msging backen d can be more fluent.
    # owner should either be the sender or recipient and other_person should be the one owner isn't  <-- 10/10 real helpful
    owner = models.ForeignKey(User, related_name='owner_msg_set',null=True)
    other_person = models.ForeignKey(User, related_name='other_msg_set',null=True)
    item = models.ForeignKey(ItemForSale, null=True, blank=True)
    post_title = models.CharField(max_length=50,default="",blank=True)
    post_id = models.IntegerField(null=True,blank=True)
    post_deleted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=True,null=True)
    messages = models.ManyToManyField("Message")
    is_read = models.BooleanField(default=True)
    newest_message_time = models.DateTimeField(null=True)
    declined = models.BooleanField(default=False)
    declined_user = models.ForeignKey(User, related_name='+', null=True, blank=True)
    # declined_user = person who got declined, e.g. Seller declines buyer means declined_user = buyer

    def get_absolute_url(self):
        return '/accounts/profile/messages/%i' % self.id
    def get_mobile_url(self):
        return '/view_messages/%i/' % self.id
        
#create ItemFlags if user flags
class ItemFlag(models.Model):
    flagger = models.ForeignKey(User) #who flagged an item
    item = models.ForeignKey(ItemForSale) #item being flagged
    def __unicode__(self):
        return self.item.title
    
class CaseInsensitiveModelBackend(ModelBackend):
    """
    By default ModelBackend does case _sensitive_ username authentication, which isn't what is
    generally expected.  This backend supports case insensitive username authentication.
    """
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(username__iexact=username)
            if user.check_password(password):
                return user
            else:
                return None
        except User.DoesNotExist:
            return None


import re

from django.db.models import Q

def normalize_query(query_string,
        findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
        normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:
        
        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    
    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 

def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    
    '''
    query = None # Query to search for every search term        
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query

class FacebookPostForExcel(models.Model):
    message = models.TextField(null=True, blank=True)
    user_id = models.BigIntegerField(null=True, blank=True)
    facebook_id = models.BigIntegerField()
    seller_name = models.TextField(blank=True, null=True)
    post_url = models.URLField(blank=True, null=True)
    thumbnail_url = models.URLField(blank=True, null=True)
    picture_url = models.URLField(blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    updated_time = models.DateTimeField(blank=True, null=True)
    num_comments = models.PositiveSmallIntegerField(null=True, blank=True)
    num_likes = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ['user_id', 'facebook_id']

class ItemReview(models.Model):
    SCORE_CHOICES = ((1,1), (2,2), (3,3), (4,4), (5,5))
    seller = models.ForeignKey(User, related_name="itemreview_seller")
    buyer = models.ForeignKey(User, related_name="itemreview_buyer")
    item = models.ForeignKey(ItemForSale)
    score = models.IntegerField(choices=SCORE_CHOICES)
    comment = models.TextField()
    time_created = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.item.title + " - " + str(self.score) + "/5 stars"
