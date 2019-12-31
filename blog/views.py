from django.urls import reverse_lazy

from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, DeleteView
from django.http import Http404
from django.shortcuts import render
from blog.models import Blog, Category, Group

from django.db.models import Count

from django.views.generic.edit import CreateView


from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required

from django.utils.decorators import method_decorator


@method_decorator(login_required, name='dispatch')
class BlogView(ListView):

    template_name = 'blog/index.html'
    model = Blog
    paginate_by = 6  # if pagination is desired
    context_object_name = 'posts'
    ordering = ['-posted']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all().annotate(posts_count=Count('blog'))
        context['groups'] = Group.objects.all().annotate(posts_count=Count('blog'))
        context['image_default'] = (
            'https://www.gumtree.com/static/1/resources/assets/rwd/images/orphans/a37b37d99e7cef805f354d47.noimage_thumbnail.png'
        )
        return context


@login_required
def view_post(request, slug):
    try:
        p = Blog.objects.get(slug=slug)
    except Blog.DoesNotExist:
        raise Http404("Post does not exist")
    return render(request, 'blog/view_post.html', {'post': p})


@login_required
def view_category(request, slug):
    try:
        category = Category.objects.get(slug=slug)
    except Category.DoesNotExist:
        raise Http404("Category does not exist")
    return render(
        request,
        'blog/view_category.html',
        {
            'category': category,
            'posts': Blog.objects.filter(category=category)[:5],
        }
    )


@login_required
def view_group(request, slug):
    try:
        group = Group.objects.get(slug=slug)
    except Group.DoesNotExist:
        raise Http404("Group does not exist")
    return render(
        request,
        'blog/view_group.html',
        {
            'group': group,
            'posts': Blog.objects.filter(groups=group)[:5],
        }
    )


@method_decorator(staff_member_required, name='dispatch')
class PostCreateView(CreateView):
    model = Blog
    fields = ['title', 'rich_body', 'author', 'category', 'groups', 'image_url']


@method_decorator(staff_member_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Blog
    fields = ['title', 'rich_body', 'author', 'category', 'groups', 'image_url']


@method_decorator(staff_member_required, name='dispatch')
class PostDeleteView(DeleteView):
    model = Blog
    success_url = reverse_lazy('blog:blog-index')
