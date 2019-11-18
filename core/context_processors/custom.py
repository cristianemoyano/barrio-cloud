from django.conf import settings
from django.urls import resolve


def breadcrumbs(request):
    """
    Context processor for include general breadcrumb in the mains views
    :return: dictionary with the breadcrumb for each view
    """
    app_name = resolve(request.path_info).app_name
    kwargs = resolve(request.path_info).kwargs
    if app_name in settings.BREADCRUMBS_VIEWS:
        return {
            'breadcrumbs': settings.BREADCRUMBS_VIEWS.get(app_name, ''),
            'kwargs': kwargs,
        }
    return {}
