from django import template
import ast
register = template.Library()

@register.simple_tag(takes_context=True)
def dict_get(context,key):
    request = context['request']
    uuid_dict = request.session.get('UUIDS', {})
    return uuid_dict.get(key)
