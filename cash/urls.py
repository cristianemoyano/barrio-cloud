from django.urls import path
from cash import views as cash_views

app_name = 'cash'

urlpatterns = [
    path('', cash_views.EntryListView.as_view(), name='cash-index'),
    path('entry/<slug:slug>/', cash_views.entry_detail_view, name='cash-view-entry'),
    path('new/', cash_views.EntryCreate.as_view(), name='cash-entry-new'),
    path('revert/<slug:slug>/', cash_views.RevertEntryView.as_view(), name='cash-entry-revert'),
]
