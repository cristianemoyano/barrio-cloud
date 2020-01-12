from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User

from cash.models import Entry, UserEntry, EntryType
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

from common.upload import upload_file


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


def get_balance_status(balance):
    zero = Money(0, balance.currency)
    if balance < zero:
        status = {
            'text': 'DEUDA',
            'style': 'danger',
        }
    elif balance == zero:
        status = {
            'text': 'SIN FONDOS',
            'style': 'warning',
        }
    else:
        status = {
            'text': 'SUPERÁVIT',
            'style': 'success',
        }
    return status


@method_decorator(login_required, name='dispatch')
class EntryListView(ListView):
    template_name = 'cash/index.html'
    model = Entry
    paginate_by = 50  # if pagination is desired
    context_object_name = 'entries'
    ordering = ['-created_date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        balance = get_new_balance(0, 'ARS')
        balance_status = get_balance_status(balance)
        context['balance_status'] = balance_status
        context['balance'] = balance
        return context


@login_required
def entry_detail_view(request, slug):
    try:
        entry = Entry.objects.get(slug=slug)
    except Entry.DoesNotExist:
        raise Http404("Entry does not exist")
    return render(request, 'cash/view_entry.html', {'entry': entry})


def get_entry_amount(amount, currency, entry_type):
    zero = Money(0, currency)
    if entry_type == 'GASTO':
        return amount if amount < zero else (amount * -1)
    elif entry_type == 'PAGO':
        return amount if amount > zero else (amount * -1)
    raise Exception('Entry type not supported')


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(login_required, name='dispatch')
class EntryCreateDebt(CreateView):
    model = Entry
    fields = ['detail', 'amount', 'notes']

    def form_valid(self, form):
        entry = form.save(commit=False)
        links = upload_file(self.request, 'attached_file')
        entry.attached_file_url = links['dropbox']
        entry.user = self.request.user
        entry.amount = get_entry_amount(entry.amount, entry.amount.currency, 'GASTO')
        entry.balance = get_new_balance(
            entry.amount,
            entry.amount.currency,
        )
        entry.entry_type = EntryType.objects.get(title='Gasto')
        entry.save()
        response = super(EntryCreateDebt, self).form_valid(form)
        return response


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(login_required, name='dispatch')
class EntryCreatePayment(CreateView):
    model = Entry
    fields = ['detail', 'amount', 'notes']

    def form_valid(self, form):
        entry = form.save(commit=False)
        links = upload_file(self.request, 'attached_file')
        entry.attached_file_url = links['dropbox']
        entry.user = self.request.user
        entry.amount = get_entry_amount(entry.amount, entry.amount.currency, 'PAGO')
        entry.balance = get_new_balance(
            entry.amount,
            entry.amount.currency,
        )
        entry.entry_type = EntryType.objects.get(title='Pago')
        entry.save()
        response = super(EntryCreatePayment, self).form_valid(form)
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
                entry_type=entry_to_revert.entry_type,
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


def get_user_entry_amount(amount, currency, entry_type):
    zero = Money(0, currency)
    if entry_type == 'GASTO':
        return amount if amount > zero else (amount * -1)
    elif entry_type == 'PAGO':
        return amount if amount < zero else (amount * -1)
    raise Exception('Entry type not supported')


def get_user_balance_status(balance):
    zero = Money(0, balance.currency)
    if balance > zero:
        status = {
            'text': 'A PAGAR',
            'style': 'warning',
        }
    elif balance == zero:
        status = {
            'text': 'AL DÍA',
            'style': 'success',
        }
    else:
        status = {
            'text': 'A FAVOR',
            'style': 'info',
        }
    return status


@method_decorator(login_required, name='dispatch')
class UserEntryListView(ListView):
    template_name = 'cash/user_index.html'
    model = UserEntry
    paginate_by = 50  # if pagination is desired
    context_object_name = 'entries'
    ordering = ['-created_date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_balance = get_new_user_balance(0, 'ARS', self.kwargs.get('user_target_id'))
        balance_status = get_user_balance_status(user_balance)
        context['balance'] = user_balance
        context['balance_status'] = balance_status
        context['member'] = User.objects.get(pk=self.kwargs.get('user_target_id'))
        return context

    def get_queryset(self):
        queryset = super(UserEntryListView, self).get_queryset()
        user_target_id = self.kwargs.get('user_target_id')
        user_entries = queryset.filter(target_user=user_target_id)
        return user_entries


@login_required
def user_entry_detail_view(request, slug):
    try:
        p = UserEntry.objects.get(slug=slug)
    except UserEntry.DoesNotExist:
        raise Http404("Entry does not exist")
    return render(request, 'cash/view_user_entry.html', {'entry': p})


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(login_required, name='dispatch')
class UserEntryCreateDebt(CreateView):
    model = UserEntry
    fields = ['detail', 'amount', 'notes']

    def form_valid(self, form):
        user_entry = form.save(commit=False)
        links = upload_file(self.request, 'attached_file')
        user_entry.attached_file_url = links['dropbox']
        user_entry.target_user = User.objects.get(pk=self.kwargs.get('user_target_id'))
        user_entry.user = self.request.user
        user_entry.amount = get_user_entry_amount(user_entry.amount, user_entry.amount.currency, 'GASTO')
        user_entry.balance = get_new_user_balance(
            user_entry.amount,
            user_entry.amount.currency,
            self.kwargs.get('user_target_id'),
        )
        user_entry.entry_type = EntryType.objects.get(title='Gasto')
        user_entry.save()
        response = super(UserEntryCreateDebt, self).form_valid(form)
        return response


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(login_required, name='dispatch')
class UserEntryCreatePayment(CreateView):
    model = UserEntry
    fields = ['detail', 'amount', 'notes']

    def form_valid(self, form):
        user_entry = form.save(commit=False)
        links = upload_file(self.request, 'attached_file')
        user_entry.attached_file_url = links['dropbox']
        user_entry.target_user = User.objects.get(pk=self.kwargs.get('user_target_id'))
        user_entry.user = self.request.user
        user_entry.amount = get_user_entry_amount(user_entry.amount, user_entry.amount.currency, 'PAGO')
        user_entry.balance = get_new_user_balance(
            user_entry.amount,
            user_entry.amount.currency,
            self.kwargs.get('user_target_id'),
        )
        user_entry.entry_type = EntryType.objects.get(title='Pago')
        user_entry.save()
        response = super(UserEntryCreatePayment, self).form_valid(form)
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
            balance = get_new_user_balance(
                reverted_amount,
                entry_to_revert.amount.currency,
                entry_to_revert.target_user.id,
            )
            reverted_entry = UserEntry.objects.create(
                detail=detail,
                amount=reverted_amount,
                balance=balance,
                user=self.request.user,
                entry_type=entry_to_revert.entry_type,
                target_user=entry_to_revert.target_user,
            )
            reverted_entry.save()
            return HttpResponseRedirect(reverse_lazy('cash:cash-user-account', args=[entry_to_revert.target_user.id]))
