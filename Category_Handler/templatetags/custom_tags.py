from django import template
from django.utils.html import format_html
from django.utils.http import urlencode
from decimal import Decimal
register = template.Library()

@register.simple_tag(takes_context=True)
def dict_get(context,key):
    request = context['request']
    uuid_dict = request.session.get('UUIDS', {})
    return uuid_dict.get(key)

@register.simple_tag
def detail_link(name):
    try:
        category, date, time, value = name.split('_', 3)
    except ValueError:
        return format_html("<span>Invalid name format</span>")
    value = str(Decimal(value))
    query_params = urlencode({
        'category': category,
        'date': date,
        'time': time,
        'value': value,
    })
    print(time)
    url = f"/In-Category/View_Bill/?{query_params}"
    return format_html('<a href="{}">{}</a>', url, name)


@register.simple_tag
def edit_link(name):
    try:
        category, date, time, value = name.split('_', 3)
    except ValueError:
        return format_html("<span>Invalid name format</span>")
    value = str(Decimal(value))
    query_params = urlencode({
        'category': category,
        'date': date,
        'time': time,
        'value': value,
    })
    print(time)
    url = f"/In-Category/Edit_Bill/?{query_params}"
    return format_html('<a href="{}">Edit</a>', url)



@register.simple_tag
def clean_edit_link(name):
    try:
        category, date, time, value = name.split('_', 3)
    except ValueError:
        return format_html("<span>Invalid name format</span>")
    value = str(Decimal(value))
    query_params = urlencode({
        'category': category,
        'date': date,
        'time': time,
        'value': value,
    })
    print(time)
    url = f"/In-Category/Clean_Edit_Bill/?{query_params}"
    return format_html('<a href="{}">Upload_image</a>', url)


