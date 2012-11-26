from django import template
from django.conf import settings

register = template.Library()


def multiupform(context):
    return {
        'static_url':settings.MEDIA_URL,
        'post_key':context['post_key'],
    }

register.inclusion_tag('multiuploader/multiuploader_main.html', takes_context=True)(multiupform)