"""Root URL configuration.

All API routes are versioned under /api/v1/ and delegated to each domain
app's `api.urls` module.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

api_v1_patterns = [
    path("auth/", include("apps.accounts.api.auth_urls")),
    path("users/", include("apps.accounts.api.user_urls")),
    path("notifications/", include("apps.notifications.api.urls")),
    path("catalog/", include("apps.catalog.api.urls")),
    path("workshops/", include("apps.workshops.api.urls")),
    path("reviews/", include("apps.reviews.api.urls")),
    path("favorites/", include("apps.workshops.api.favorite_urls")),
    path("service-requests/", include("apps.requests.api.urls")),
    path("search/", include("apps.search.api.urls")),
    path("admin/", include("apps.administration.api.urls")),
]

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/", include(api_v1_patterns)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
