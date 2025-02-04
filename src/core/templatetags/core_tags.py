from asgiref.sync import sync_to_async
from avatar.templatetags.avatar_tags import avatar as avatar_tag
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


def sync_avatar(user, size=80):
    """Synchronous wrapper for the avatar template tag"""
    return avatar_tag(user, size)


@register.simple_tag
def async_avatar(user, size=80):
    """Async-friendly avatar tag"""
    # We'll use sync_to_async with thread_sensitive=True to avoid database errors
    async_get_avatar = sync_to_async(sync_avatar, thread_sensitive=True)
    # We'll use sync_to_async's __call__ to get the result immediately
    result = async_get_avatar(user, size)
    return mark_safe(result)
