from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.contrib.auth.models import User
from django.db.models import Q
from functools import reduce


@method_decorator(login_required, name='dispatch')
class MembersView(ListView):

    template_name = 'members/index.html'
    model = User
    paginate_by = 6  # if pagination is desired
    context_object_name = 'members'
    # ordering = ['-posted']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        fields = [m.name for m in self.model._meta.fields]
        result = super(MembersView, self).get_queryset()
        query = self.request.GET.get('q')
        if query:
            result = result.filter(
                reduce(lambda x, y: x | Q(**{"{}__icontains".format(y): query}), fields, Q())
            )
        return result
