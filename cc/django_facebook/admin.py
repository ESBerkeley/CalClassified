from django.contrib import admin
from django_facebook import models


class FacebookUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'name', 'facebook_id',)
    search_fields = ('name',)

class FacebookLikeAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'name', 'category', 'facebook_id',)
    search_fields = ('name',)
    filter_fields = ('category', )

class FacebookGroupAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'name', 'bookmark_order', 'facebook_id',)
    search_fields = ('name',)
    filter_fields = ('bookmark_order', )

admin.site.register(models.FacebookUser, FacebookUserAdmin)
admin.site.register(models.FacebookLike, FacebookLikeAdmin)
admin.site.register(models.FacebookGroup, FacebookGroupAdmin)