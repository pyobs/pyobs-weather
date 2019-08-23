from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import OverView

urlpatterns = [
    path('', OverView.as_view()),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
