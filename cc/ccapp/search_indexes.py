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
    
    category = indexes.MultiValueField()
    circles = indexes.MultiValueField()
        
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