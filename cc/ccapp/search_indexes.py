import datetime
from haystack import indexes
from haystack import site
from models import *


class ItemForSaleIndex(indexes.RealTimeSearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title', boost=1.5)
    #IFS
    price = indexes.FloatField(model_attr='price') #purposely not decimal field as its bugged
    #POST
    owner = indexes.CharField(model_attr='owner')
    time_created = indexes.DateTimeField(model_attr='time_created')

    pending_buyer = indexes.CharField(model_attr='pending_buyer', null=True)
    pending_flag = indexes.BooleanField(model_attr='pending_flag')
    
    category = indexes.MultiValueField()
    circles = indexes.MultiValueField()
    approved = indexes.BooleanField(model_attr='approved')
    is_facebook_post = indexes.BooleanField(model_attr='is_facebook_post')

    def prepare_approved(self, obj):
        if obj.approved==False:
            return ''
        return True

    def prepare_is_facebook_post(self, obj):
        if obj.is_facebook_post==False:
            return ''
        return True

    def prepare_category(self, obj):
        return [obj.category.id]
    
    def prepare_circles(self, obj):
        return [circle.pk for circle in obj.circles.all()]

    def get_model(self):
        return ItemForSale

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(time_created__lte=datetime.datetime.now())
        
        
site.register(ItemForSale, ItemForSaleIndex)
