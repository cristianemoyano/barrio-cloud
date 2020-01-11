from django.urls import path
from cash import views as cash_views

app_name = 'cash'

urlpatterns = [
    path('', cash_views.EntryListView.as_view(), name='cash-index'),
    path('entry/<slug:slug>/', cash_views.entry_detail_view, name='cash-view-entry'),
    path('entry/new/payment/', cash_views.EntryCreatePayment.as_view(), name='cash-entry-new-payment'),
    path('entry/new/debt/', cash_views.EntryCreateDebt.as_view(), name='cash-entry-new-debt'),
    path('revert/<slug:slug>/', cash_views.RevertEntryView.as_view(), name='cash-entry-revert'),
    # User entries
    path('user_entry/<int:user_target_id>/', cash_views.UserEntryListView.as_view(), name='cash-user-account'),
    path('user_entry/<slug:slug>/', cash_views.user_entry_detail_view, name='cash-view-user-entry'),
    path(
        'user_entry/new/payment/<int:user_target_id>/',
        cash_views.UserEntryCreatePayment.as_view(),
        name='cash-user-entry-new-payment',
    ),
    path(
        'user_entry/new/debt/<int:user_target_id>/',
        cash_views.UserEntryCreateDebt.as_view(),
        name='cash-user-entry-new-debt'
    ),
    path('user_entry/revert/<slug:slug>/', cash_views.RevertUserEntryView.as_view(), name='cash-user-entry-revert'),
]
