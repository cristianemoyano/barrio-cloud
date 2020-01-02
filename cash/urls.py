from django.urls import path
from cash import views as cash_views

app_name = 'cash'

urlpatterns = [
    path('', cash_views.EntryListView.as_view(), name='cash-index'),
    path('entry/<slug:slug>/', cash_views.entry_detail_view, name='cash-view-entry'),
    path('new/', cash_views.EntryCreate.as_view(), name='cash-entry-new'),
    path('revert/<slug:slug>/', cash_views.RevertEntryView.as_view(), name='cash-entry-revert'),
    # User entries
    path('user_entry/<int:user_target_id>/', cash_views.UserEntryListView.as_view(), name='cash-user-account'),
    path('user_entry/<slug:slug>/', cash_views.user_entry_detail_view, name='cash-view-user-entry'),
    path('user_entry/new/<int:user_target_id>/', cash_views.UserEntryCreate.as_view(), name='cash-user-entry-new'),
    path('user_entry/revert/<slug:slug>/', cash_views.RevertUserEntryView.as_view(), name='cash-user-entry-revert'),
]
