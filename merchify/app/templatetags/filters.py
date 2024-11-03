from django import template

register = template.Library()

@register.filter
def multiply(a, b):
    result = (a * b)
    return format(result, '.2f')

@register.filter
def range_filter(value):
    return range(value)