from django import template

register = template.Library()

@register.filter
def times(number):
    """Returns a range from 0 to number for looping in templates"""
    return range(number)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

