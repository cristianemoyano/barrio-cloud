from django.urls import path, include
from accounts import views as accounts_views

app_name = 'accounts'

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('profile/', accounts_views.profile, name='user-profile'),
]
