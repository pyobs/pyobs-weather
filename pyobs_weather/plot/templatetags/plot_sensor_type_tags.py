from datetime import datetime, timedelta

from plotly import offline
import plotly.graph_objs as go
from django import template
import pandas as pd

from pyobs_weather.weather.models import Station, SensorType, Sensor, Value

register = template.Library()


@register.inclusion_tag('plot/sensor_type.html')
def plot_sensor_type(sensor_type, start=None, end=None):
    # start and end
    if start is None or end is None:
        end = datetime.utcnow()
        start = end - timedelta(days=1)

    # get sensor type
    print(sensor_type)
    st = SensorType.objects.get(code=sensor_type)

    # init figure
    fig = go.Figure()

    # loop all sensors with this type
    for sensor in Sensor.objects.filter(type=st).all():
        # don't plot it?
        if not sensor.station.plot:
            continue

        # get data points
        values = Value.objects.filter(sensor=sensor, time__gte=start, time__lte=end).order_by('-time')
        print(values)

        # add plot
        fig.add_trace(go.Scatter(
            x=[v.time for v in values],
            y=[v.value for v in values],
            name=sensor.station.name,
            line={'color': sensor.station.color}
        ))

    # set layout
    fig.update_layout(
        # title=go.layout.Title(text=st.name),
        autosize=True,
        height=300,
        margin=dict(l=70, r=0, t=30, b=10),
        xaxis=go.layout.XAxis(
            title=go.layout.xaxis.Title(text='Time [UT]')
        ),
        yaxis=go.layout.YAxis(
            title=go.layout.yaxis.Title(text='%s [%s]' % (st.name, st.unit))
        )
    )

    # Add plot to the template context
    return {'figure': offline.plot(fig, output_type='div', show_link=False)}
