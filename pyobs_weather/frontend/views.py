from pathlib import Path

from django.http import HttpResponse, HttpResponseNotFound

# Built Vue SPA entry point (produced by `npm run build` in frontend-vue/).
INDEX_PATH = Path(__file__).resolve().parent / "static" / "frontend" / "dist" / "index.html"


def index(request):
    """Serve the Vue SPA's built index.html for the single-page app routes."""
    try:
        return HttpResponse(INDEX_PATH.read_text(), content_type="text/html")
    except FileNotFoundError:
        return HttpResponseNotFound(
            "Frontend not built. Run `npm run build` in the frontend-vue/ directory.",
            content_type="text/plain",
        )
