from django import template

register = template.Library()

@register.filter(name='divide')
def divide(value, arg):
    try:
        return value / arg
    except (TypeError, ZeroDivisionError):
        return value