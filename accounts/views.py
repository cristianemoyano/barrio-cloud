from django.http import Http404
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render

from django.views import View

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.contrib.auth.models import User
from .models import Profile

from common.upload import upload_file


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


@method_decorator(login_required, name='dispatch')
class ChangeImageProfileView(View):
    initial = {'key': 'value'}
    template_name = 'accounts/change_image_form.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'initial': self.initial})

    def post(self, request, *args, **kwargs):
        profile = Profile.objects.get_or_create(user=self.request.user)
        profile = profile[0]
        links = upload_file(self.request, 'attached_file', ['image/png', 'image/jpeg'])
        profile.image_url = links['dropbox']
        profile.save()
        return HttpResponseRedirect(reverse_lazy('accounts:user-profile'))
