from django.urls import reverse_lazy
from django.http import HttpResponseRedirect

from cash.models import Entry
from cash.forms import RevertEntryForm

from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views import View

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
from django.shortcuts import render

from django.utils.decorators import method_decorator

from djmoney.money import Money
from tzlocal import get_localzone


def get_new_balance(new_amount, currency):
    try:
        latest = Entry.objects.latest('created_date')
    except Entry.DoesNotExist:
        latest = None
    balance = Money(0, currency)
    if latest:
        balance += latest.balance + new_amount
    else:
        balance += new_amount
    return balance


@method_decorator(login_required, name='dispatch')
class EntryListView(ListView):
    template_name = 'cash/index.html'
    model = Entry
    paginate_by = 50  # if pagination is desired
    context_object_name = 'entries'
    ordering = ['-created_date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_time_zone'] = get_localzone()
        context['balance'] = get_new_balance(0, 'ARS')
        return context


@login_required
def entry_detail_view(request, slug):
    try:
        p = Entry.objects.get(slug=slug)
    except Entry.DoesNotExist:
        raise Http404("Entry does not exist")
    return render(request, 'cash/view_entry.html', {'entry': p})


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(login_required, name='dispatch')
class EntryCreate(CreateView):
    model = Entry
    fields = ['detail', 'amount', 'entry_type', 'attached_file_url', 'notes']

    def form_valid(self, form):
        entry = form.save(commit=False)
        entry.user = self.request.user
        entry.balance = get_new_balance(entry.amount, entry.amount.currency)
        entry.save()
        response = super(EntryCreate, self).form_valid(form)
        return response


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(login_required, name='dispatch')
class RevertEntryView(View):
    form_class = RevertEntryForm
    template_name = 'cash/revert_entry.html',

    def get(self, request, slug):
        form = self.form_class()
        try:
            entry = Entry.objects.get(slug=slug)
        except Entry.DoesNotExist:
            raise Http404("Entry does not exist")
        return render(request, self.template_name, {'entry': entry, 'form': form})

    def post(self, request, slug):
        form = self.form_class(request.POST)
        try:
            entry_to_revert = Entry.objects.get(slug=slug)
        except Entry.DoesNotExist:
            raise Http404("Entry does not exist")
        if form.is_valid():
            detail = 'reverted-({})'.format(entry_to_revert.detail)
            reverted_amount = entry_to_revert.amount * (-1)
            balance = get_new_balance(reverted_amount, entry_to_revert.amount.currency)
            reverted_entry = Entry.objects.create(
                detail=detail,
                amount=reverted_amount,
                balance=balance,
                user=self.request.user,
            )
            reverted_entry.save()
            return HttpResponseRedirect(reverse_lazy('cash:cash-index'))
