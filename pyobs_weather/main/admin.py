from django.contrib import admin

from pyobs_weather.main.models import Station, SensorType, Sensor, Evaluator

admin.site.register(Station)
admin.site.register(SensorType)
admin.site.register(Sensor)
admin.site.register(Evaluator)
