from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.contrib.auth.models import User
from accounts.models import Profile
from django.db.models import Q
from functools import reduce


@method_decorator(login_required, name='dispatch')
class MembersView(ListView):

    template_name = 'members/index.html'
    model = User
    paginate_by = 6  # if pagination is desired
    context_object_name = 'members'
    valid_profile_fields = ['first_name', 'last_name', 'dni', 'telephone', 'email']
    # ordering = ['-posted']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        user_fields = [m.name for m in self.model._meta.fields]
        profile_fields = [m.name for m in Profile._meta.fields]
        profile_searcheable_fields = []
        for profile_field in profile_fields:
            if profile_field in self.valid_profile_fields:
                profile_searcheable_fields.append(profile_field)
        profiles_queryset = Profile.objects.all()
        users_queryset = super(MembersView, self).get_queryset()
        query = self.request.GET.get('q')
        result = users_queryset
        if query:
            result = users_queryset.filter(
                reduce(lambda x, y: x | Q(**{"{}__icontains".format(y): query}), user_fields, Q())
            )
            if not result:
                result = profiles_queryset.filter(
                    reduce(lambda x, y: x | Q(**{"{}__icontains".format(y): query}), profile_searcheable_fields, Q())
                )
        return result
