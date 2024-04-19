from django import template
from decimal import Decimal
from django.utils.timesince import timesince
from django.utils.timezone import now

register = template.Library()

@register.filter
def subtract(value, arg):
    if isinstance(value, Decimal) and isinstance(arg, float):
        value = float(value)
    elif isinstance(value, float) and isinstance(arg, Decimal):
        arg = float(arg)
        
    return value - arg


    # Inside your_app/templatetags/custom_filters.py



@register.filter
def custom_timesince(value):
    """
    Custom template filter to display time elapsed since a timestamp
    in a human-readable format.
    """
    time_difference = now() - value
    seconds = time_difference.total_seconds()

    if seconds < 60:
        return f"{int(seconds)} secs ago"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} {'mins' if minutes == 1 else 'mins'} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} {'hr' if hours == 1 else 'hr'} ago"
    else:
        return timesince(value) + " ago"
