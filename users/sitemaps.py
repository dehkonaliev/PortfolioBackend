from django.contrib.sitemaps import Sitemap
from .models import CustomUser

class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return CustomUser.objects.all()

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        # points to the React route, not a Django template
        return f"/users/{obj.username}/"