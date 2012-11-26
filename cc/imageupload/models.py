from django.db import models
from django import forms
from django.contrib import admin
from django.forms import ModelForm
from stdimage import StdImageField
from ccapp.models import ItemForSale

class UploadImage(models.Model):
    title = models.CharField(max_length=50)	
    imgfile = StdImageField(upload_to='images', size = (640,480,True), thumbnail_size = (100,100,True), blank = True)
    post = models.ForeignKey('ccapp.ItemForSale', default = ItemForSale.objects.filter(pk=1), related_name = 'image_sets')
    def __unicode__(self):
        return self.title

class UploadImageForm(forms.Form):
    """class Meta:
    model = UploadImage"""
    title = forms.CharField(max_length=50)
    imgfile  = forms.ImageField(label='Select a file',
    help_text='max. 10 megabytes')

admin.site.register(UploadImage)
