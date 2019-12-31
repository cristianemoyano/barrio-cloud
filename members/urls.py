from django.urls import path
from members import views as members_views

app_name = 'members'

urlpatterns = [
    path('', members_views.MembersView.as_view(), name='members-index'),
]
