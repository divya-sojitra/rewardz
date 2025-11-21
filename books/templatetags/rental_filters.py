from django import template

register = template.Library()

@register.filter
def cents_to_dollars(cents):
    """Convert cents (integer) to dollars (decimal)"""
    if cents is None:
        return 0.00
    return cents / 100.0
