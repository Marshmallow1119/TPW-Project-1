from django import template
from app.models import Clothing, CD, Vinil, Accessory

register = template.Library()

@register.filter
def multiply(a, b):
    result = (a * b)
    return format(result, '.2f')

@register.filter
def range_filter(value):
    return range(value)


@register.filter
def instanceof(value, arg):
    model_classes = {
        "Clothing": Clothing,
        "CD": CD,
        "Vinil": Vinil,
        "Accessory": Accessory,
    }

    model_class = model_classes.get(arg)
    if model_class:
        return isinstance(value, model_class)
    return False  # Return False if the arg is not a recognized type

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})