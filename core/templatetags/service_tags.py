"""
Custom template tags and filters for Smart Local Service Connect
Helper for rendering star ratings and formatted numbers cleanly.
"""

from django import template

register = template.Library()


@register.filter(name='render_stars')
def render_stars(rating):
    """
    Renders unicode stars based on numeric rating (1 to 5).
    Example: 4 -> '★★★★☆', 4.8 -> '★★★★★'
    """
    if rating is None or rating == "":
        return ""
    try:
        val = float(rating)
        rounded = round(val)
        rounded = max(0, min(5, rounded))
        return "★" * rounded + "☆" * (5 - rounded)
    except (ValueError, TypeError):
        return ""


@register.filter(name='format_rating')
def format_rating(rating):
    """Formats numeric rating to 1 decimal place or returns 'New'."""
    if rating is None or rating == "":
        return "New"
    try:
        return f"{float(rating):.1f}"
    except (ValueError, TypeError):
        return "New"
