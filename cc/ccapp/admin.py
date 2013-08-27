from django.db import models
from django.contrib import admin
from models import *
from django_facebook.models import FacebookProfile
	
class ItemForSaleAdmin(admin.ModelAdmin):
    list_display = ('title', 'time_created', 'owner', 'price', 'category')
    list_filter = ['time_created', 'pending_flag', 'sold', 'deleted', 'approved', 'category__name', 'price']
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

class FacebookProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'facebook_name', 'image',)
    list_filter = ('gender', 'user__date_joined', 'user__last_login')
    search_fields = ('facebook_name', 'user__username')
    #date_hierarchy = 'user__last_login'

class FacebookPostForExcelAdmin(admin.ModelAdmin):
    list_display = ('message', 'updated_time', 'seller_name', 'price', 'num_likes', 'num_comments')
    list_filter = ['updated_time', 'num_likes', 'num_comments']
    readonly_fields = ['updated_time']
    search_fields = ['message', 'seller_name']
    date_hierarchy = 'updated_time'

admin.site.register(Category)
admin.site.register(Circle)
admin.site.register(ItemForSale, ItemForSaleAdmin)
admin.site.register(Notification)
admin.site.register(Message)
admin.site.register(ItemReview)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(FacebookProfile, FacebookProfileAdmin)
admin.site.register(FacebookPostForExcel, FacebookPostForExcelAdmin)