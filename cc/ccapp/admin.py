from django.db import models
from django.contrib import admin
from models import *
from django_facebook.models import FacebookProfile
	
class ItemForSaleAdmin(admin.ModelAdmin):
    list_display = ('title', 'time_created', 'owner', 'price', 'category')
    list_filter = ['time_created', 'pending_flag', 'sold', 'deleted', 'approved', 'category__name',]
    readonly_fields = ['time_created', 'pending_buyer']
    search_fields = ['title', 'body', 'category__name', 'owner__first_name', 'owner__last_name']
    date_hierarchy = 'time_created'

class CommentAdmin(admin.ModelAdmin):
    search_fields = ('item__title', 'body', 'seller_response')
    list_filter = ('time_created',)
    list_display = ('body', 'item', 'sender', 'time_created')
    date_hierarchy = 'time_created'

class ThreadAdmin(admin.ModelAdmin):
    list_display = ('post_title', 'owner', 'other_person', 'timestamp', 'newest_message_time')

admin.site.register(Category)
admin.site.register(Circle)
admin.site.register(ItemForSale, ItemForSaleAdmin)
admin.site.register(Notification)
admin.site.register(Message)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(FacebookProfile)
