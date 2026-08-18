from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static

from .views import index

urlpatterns = [
    # SPA fallback: serve the Vue app for every path except the API, admin, and static files, so
    # vue-router history-mode reloads work. Django's URL resolver tries this include first, so the
    # negative lookahead is what keeps /api/ and /admin/ routing to their own includes.
    re_path(r"^(?!api/|admin/|static/).*$", index, name="index"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
