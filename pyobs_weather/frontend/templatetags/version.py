from django import template
from pyobs_weather.version import VERSION

register = template.Library()


@register.simple_tag
def version():
    return VERSION
