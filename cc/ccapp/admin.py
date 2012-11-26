from django.db import models
from django.contrib import admin
from models import Category, Circle, ItemForSale, Notification, ItemForSaleAdmin
	
class ItemForSaleAdmin(admin.ModelAdmin):
    readonly_fields = ['time_created']


admin.site.register(Category)
admin.site.register(Circle)
admin.site.register(ItemForSale, ItemForSaleAdmin)
admin.site.register(Notification)

