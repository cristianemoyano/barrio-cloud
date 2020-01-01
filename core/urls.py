
from django.urls import path, include
from django.conf.urls import url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('members/', include('members.urls')),
    path('cash/', include('cash.urls')),
    path('', include('blog.urls')),
    url(r'^tz_detect/', include('tz_detect.urls')),
]
