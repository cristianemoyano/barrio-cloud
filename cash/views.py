from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User

from cash.models import Entry, UserEntry
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


def get_new_user_balance(new_amount, currency, target_user_id):
    try:
        latest = UserEntry.objects.filter(target_user=target_user_id).latest('created_date')
    except UserEntry.DoesNotExist:
        latest = None
    balance = Money(0, currency)
    if latest:
        balance += latest.balance + new_amount
    else:
        balance += new_amount
    return balance


@method_decorator(login_required, name='dispatch')
class UserEntryListView(ListView):
    template_name = 'cash/user_index.html'
    model = UserEntry
    paginate_by = 50  # if pagination is desired
    context_object_name = 'entries'
    ordering = ['-created_date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['balance'] = get_new_user_balance(0, 'ARS', self.kwargs.get('user_target_id'))
        context['member'] = User.objects.get(pk=self.kwargs.get('user_target_id'))
        return context

    def get_queryset(self):
        queryset = super(UserEntryListView, self).get_queryset()
        use_target_id = self.kwargs.get('use_target_id')
        if use_target_id:
            queryset = queryset.filter(target_user=use_target_id)
        return queryset


@login_required
def user_entry_detail_view(request, slug):
    try:
        p = UserEntry.objects.get(slug=slug)
    except UserEntry.DoesNotExist:
        raise Http404("Entry does not exist")
    return render(request, 'cash/view_user_entry.html', {'entry': p})


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(login_required, name='dispatch')
class UserEntryCreate(CreateView):
    model = UserEntry
    fields = ['detail', 'amount', 'entry_type', 'attached_file_url', 'notes']

    def form_valid(self, form):
        user_entry = form.save(commit=False)
        user_entry.target_user = User.objects.get(pk=self.kwargs.get('user_target_id'))
        user_entry.user = self.request.user
        user_entry.balance = get_new_user_balance(
            user_entry.amount,
            user_entry.amount.currency,
            self.kwargs.get('user_target_id'),
        )
        user_entry.save()
        response = super(UserEntryCreate, self).form_valid(form)
        return response


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(login_required, name='dispatch')
class RevertUserEntryView(View):
    form_class = RevertEntryForm
    template_name = 'cash/revert_user_entry.html',

    def get(self, request, slug):
        form = self.form_class()
        try:
            entry = UserEntry.objects.get(slug=slug)
        except UserEntry.DoesNotExist:
            raise Http404("Entry does not exist")
        return render(request, self.template_name, {'entry': entry, 'form': form})

    def post(self, request, slug):
        form = self.form_class(request.POST)
        try:
            entry_to_revert = UserEntry.objects.get(slug=slug)
        except UserEntry.DoesNotExist:
            raise Http404("Entry does not exist")
        if form.is_valid():
            detail = 'reverted-({})'.format(entry_to_revert.detail)
            reverted_amount = entry_to_revert.amount * (-1)
            balance = get_new_user_balance(reverted_amount, entry_to_revert.amount.currency)
            reverted_entry = UserEntry.objects.create(
                detail=detail,
                amount=reverted_amount,
                balance=balance,
                user=self.request.user,
            )
            reverted_entry.save()
            return HttpResponseRedirect(reverse_lazy('cash:cash-user-index'))
