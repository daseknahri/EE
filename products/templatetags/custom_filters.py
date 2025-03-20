from django import template

register = template.Library()

@register.filter(name='divide')
def divide(value, arg):
    try:
        return value / arg
    except (TypeError, ZeroDivisionError):
        return value
    

@register.filter(name='linebreaks_to_br')
def linebreaks_to_br(value):
    """
    Converts newlines to <br> tags in the text.
    """
    return value.replace("\n", "<br>")