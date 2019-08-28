from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from pyobs_weather.api import views

urlpatterns = [
    path('current/', views.current, name='current'),
    path('stations/', views.stations_list, name='stations_list'),
    path('stations/<str:station_code>/', views.station_detail, name='station_detail'),
    path('stations/<str:station_code>/<str:sensor_code>/', views.sensor_detail, name='sensor_detail'),
    path('history/<str:sensor_type>/', views.history, name='history')
]