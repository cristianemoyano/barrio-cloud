from django.urls import path, include
from django.urls import reverse_lazy
from accounts import views as accounts_views

from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [

    # change password urls
    path(
        'password_change/',
        auth_views.PasswordChangeView.as_view(
            success_url=reverse_lazy('accounts:password_change_done')
        ),
        name='password_change'
    ),
    path('', include('django.contrib.auth.urls')),

    path('profile/', accounts_views.profile, name='user-profile'),
    path('detail/<int:pk>/', accounts_views.account, name='user-account'),
]
