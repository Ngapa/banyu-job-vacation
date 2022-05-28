from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include, re_path


urlpatterns = [
    path("", include("job.urls", namespace="job")),
    path("", include("account.urls", namespace="account")),
    path('admin/', admin.site.urls),
]
