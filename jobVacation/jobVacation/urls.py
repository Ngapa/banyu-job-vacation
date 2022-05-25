from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include, re_path

lang_patterns = i18n_patterns(path("", include("jobsapp.urls")),
                              path("", include("accounts.urls")),
                              )

urlpatterns = lang_patterns + [
    re_path(r"^i18n/", include("django.conf.urls.i18n")),
    path('admin/', admin.site.urls),
]
