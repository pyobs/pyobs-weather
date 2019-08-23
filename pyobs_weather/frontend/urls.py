from django.urls import path

from .views import OverView

urlpatterns = [
    path('', OverView.as_view()),
]
