import re

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.template.loader import render_to_string
from django.views import View

from users.models import CustomUser

# User agents that request a page to build a link preview / snippet.
# These bots do not execute JavaScript, so they must be served a fully
# rendered HTML document with the correct Open Graph meta tags.
CRAWLER_PATTERN = re.compile(
    r"telegrambot|facebookexternalhit|facebookcatalog|twitterbot|"
    r"twitterexternalhit|whatsapp|linkedinbot|slackbot|discordbot|"
    r"vkshare|pinterest|redditbot|xing|pocket|baiduspider|bingbot|"
    r"googlebot|google-inspectiontool|applebot|rogerbot|embedly|"
    r"quora link preview|showyoubot|tumblr|skypeuripreview|flipboard|"
    r"bitlybot|nuzzel|outbrain|duckduckbot|yandex|bytespider|amazonbot|"
    r"slurp|curl",
    re.IGNORECASE,
)


def _absolute_media_url(path):
    """Turn a storage-relative URL into a full public URL."""
    if not path:
        return None
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return settings.FRONTEND_URL.rstrip("/") + path


def _home_context():
    base = settings.FRONTEND_URL.rstrip("/")
    return {
        "title": "MyResume — Create your portfolio and get discovered",
        "description": (
            "Create a stunning resume and project portfolio. "
            "Get discovered by employers searching for talent across every field."
        ),
        "image": base + "/cover.jpg",
        "url": base + "/",
        "og_type": "website",
    }


def _profile_context(user):
    base = settings.FRONTEND_URL.rstrip("/")
    full_name = " ".join(filter(None, [user.first_name, user.last_name])) or user.username
    title = f"{full_name} — {user.job_title}" if user.job_title else full_name
    description = user.summary or " · ".join(filter(None, [user.job_title, f"@{user.username}"]))
    image = None
    photo = user.profile_photo or user.profile_thumbnail
    if photo:
        image = _absolute_media_url(photo.url)
    if not image:
        image = base + "/cover.jpg"
    return {
        "title": title,
        "description": description,
        "image": image,
        "url": f"{base}/{user.username}",
        "og_type": "profile",
    }


class SocialPreviewView(View):
    """Serves a pre-rendered HTML page for social crawlers.

    Only reachable for non-/api, non-/admin GET requests from known crawler
    user agents (see nginx.conf mapping). Browsers are served the SPA by the
    static frontend and never hit this view.
    """

    http_method_names = ["get"]

    def get(self, request):
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        if not CRAWLER_PATTERN.search(user_agent):
            return HttpResponseNotFound("Not found")

        path = request.path.strip("/")
        if not path or "." in path:
            context = _home_context()
        else:
            username = path.split("/")[0]
            user = CustomUser.objects.filter(username=username).only(
                "username", "first_name", "last_name", "job_title",
                "summary", "profile_photo", "profile_thumbnail",
            ).first()
            context = _profile_context(user) if user else _home_context()

        html = render_to_string("social/preview.html", context)
        response = HttpResponse(html)
        response["Content-Type"] = "text/html; charset=utf-8"
        response["Cache-Control"] = "public, max-age=300"
        response["Vary"] = "User-Agent"
        return response