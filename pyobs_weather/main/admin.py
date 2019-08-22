from django.contrib import admin

from pyobs_weather.main.models import Station, Weather

admin.site.register(Station)
admin.site.register(Weather)
