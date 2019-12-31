from django.http import Http404
from django.shortcuts import render

from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User


@login_required
def profile(request):
    try:
        user = User.objects.get(pk=request.user.pk)
    except User.DoesNotExist:
        raise Http404("User does not exist")
    return render(request, 'accounts/profile.html', {'user': user})


@login_required
def account(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        raise Http404("User does not exist")
    return render(request, 'accounts/profile.html', {'user': user})
