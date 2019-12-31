
from django.urls import path, include
from django.conf.urls import url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('members/', include('members.urls')),
    path('', include('blog.urls')),
]
