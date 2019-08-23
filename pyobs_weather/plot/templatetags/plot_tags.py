from plotly import offline
import plotly.graph_objs as go
from django import template

from pyobs_weather.weather.models import Weather

register = template.Library()


@register.inclusion_tag('plot/weather.html')
def weather(weather):
    # order weather by creation date
    weather = weather.order_by('-time')
    # x axis: target names. y axis: datum count
    data = [go.Scatter(
        x=[w.time for w in weather],
        y=[w.temp for w in weather]
    )]
    # Create the plot
    figure = offline.plot(go.Figure(data=data), output_type='div', show_link=False)
    # Add plot to the template context
    return {'figure': figure}
