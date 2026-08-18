from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static

from .views import index

urlpatterns = [
    # SPA fallback: serve the Vue app for every path except the API, admin, and static files, so
    # vue-router history-mode reloads work. Django's URL resolver tries this include first, so the
    # negative lookahead is what keeps /api/, /admin/, and /static/ routing to their own includes.
    # The bare (no trailing slash) forms are excluded too, so Django's APPEND_SLASH redirect
    # (e.g. /admin -> /admin/) still fires instead of the SPA swallowing the request.
    re_path(r"^(?!api/|api$|admin/|admin$|static/|static$).*$", index, name="index"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
