from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import OverView, Documentation, SensorsView

urlpatterns = [
    path('', OverView.as_view(), name='home'),
    path('sensors/', SensorsView.as_view(), name='sensors'),
    path('docs/', Documentation.as_view(), name='docs'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
