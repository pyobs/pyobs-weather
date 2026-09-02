from pathlib import Path

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.utils.html import escapejs
from django.views.decorators.csrf import ensure_csrf_cookie

# Built Vue SPA entry point (produced by `npm run build` in frontend-vue/).
INDEX_PATH = Path(__file__).resolve().parent / "static" / "frontend" / "dist" / "index.html"

# Placeholder baked into asset URLs by frontend-vue/vite.config.ts, since ROOT_URL is only known
# at container runtime, not at image build time.
STATIC_BASE_PLACEHOLDER = "/__PYOBS_STATIC_BASE__/frontend/dist/"


@ensure_csrf_cookie
def index(request):
    """Serve the Vue SPA's built index.html for the single-page app routes."""
    try:
        html = INDEX_PATH.read_text()
    except FileNotFoundError:
        return HttpResponseNotFound(
            "Frontend not built. Run `npm run build` in the frontend-vue/ directory.",
            content_type="text/plain",
        )

    # rewrite the placeholder asset base to the real (ROOT_URL-aware) static URL, and hand the
    # SPA its root URL so vue-router and the API client can build correct paths under ROOT_URL.
    html = html.replace(STATIC_BASE_PLACEHOLDER, settings.STATIC_URL + "frontend/dist/")
    html = html.replace(
        "<head>",
        f'<head>\n    <script>window.__PYOBS_ROOT_URL__ = "{escapejs(settings.ROOT_URL)}";</script>',
        1,
    )
    return HttpResponse(html, content_type="text/html")
