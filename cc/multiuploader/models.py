from django.db import models
import random

from django.conf import settings
try:
    storage = settings.MULTI_IMAGES_FOLDER+'/'
except AttributeError:
    storage = 'multiuploader_images/'

#from stdimage import StdImageField
from ccapp.models import ItemForSale
from sorl.thumbnail import ImageField
from django_resized import ResizedImageField
    
def content_file_name(instance, filename):
    return '/'.join([ 'users',instance.post.owner.username,'images',filename])
    
class MultiuploaderImage(models.Model):
    """Model for storing uploaded photos"""
    filename = models.CharField(max_length=60, blank=True, null=True)
    #image = models.ImageField(upload_to=storage)
    image = ResizedImageField(upload_to=content_file_name) #used to be storage
    #image = StdImageField(upload_to=storage, size = (640,480,True), thumbnail_size = (100,100,True), blank = True)
    key_data = models.CharField(max_length=90, unique=True, blank=True, null=True) #SEUNG REMOVED THIS
    upload_date = models.DateTimeField(auto_now_add=True)
    post_key_data = models.CharField(max_length=30, blank=True, null=True)
    post = models.ForeignKey('ccapp.ItemForSale', blank=True, null=True, related_name = 'image_set')

    @property
    def key_generate(self):
        """returns a string based unique key with length 80 chars"""
        while 1:
            key = str(random.getrandbits(256))
            try:
                MultiuploaderImage.objects.get(key=key)
            except:
                return key

    def __unicode__(self):
        return self.image.name
        
    def delete(self): #delete image on server
        self.image.delete()
        super(MultiuploaderImage, self).delete()
        


