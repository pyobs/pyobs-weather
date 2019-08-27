from django import template

from pyobs_weather.weather.models import SensorType

register = template.Library()


@register.inclusion_tag('plot/sensor_type.html')
def plot_sensor_type(sensor_type):
    st = SensorType.objects.get(code=sensor_type)
    return {'type': sensor_type, 'name': st.name, 'unit': st.unit}
