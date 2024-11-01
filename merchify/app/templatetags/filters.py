from django import template

register = template.Library()

@register.filter
def multiply(a, b):
    result = (a * b)
    return format(result, '.2f')