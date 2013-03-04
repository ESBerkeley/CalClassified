from django.db import models
from django.contrib import admin
from models import *
from django_facebook.models import FacebookProfile
	
class ItemForSaleAdmin(admin.ModelAdmin):
    readonly_fields = ['time_created']


admin.site.register(Category)
admin.site.register(Circle)
admin.site.register(ItemForSale, ItemForSaleAdmin)
admin.site.register(Notification)
admin.site.register(Message)
admin.site.register(Thread)
admin.site.register(Comment)
admin.site.register(FacebookProfile)
